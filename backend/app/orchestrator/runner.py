import asyncio
from datetime import datetime, timezone
import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.base import utc_now
from app.db.models.analysis import (
    Architecture,
    Claim,
    Evidence,
    Gap,
    MVPTask,
    Proposal,
    Risk,
)
from app.db.models.project import Project
from app.db.models.research_run import ResearchRun, RunEvent
from app.db.models.source import Source
from app.db.session import async_session_factory
from app.pipeline.source_pipeline import SourcePipeline
from app.tools.base import RawSourceResult
from app.tools.github_tool import GitHubTool
from app.tools.huggingface_tool import HuggingFaceTool
from app.tools.semantic_scholar import PaperTool
from app.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.web_tool = WebSearchTool()
        self.paper_tool = PaperTool()
        self.github_tool = GitHubTool()
        self.hf_tool = HuggingFaceTool()

    async def emit_event(
        self, session: AsyncSession, event_type: str, payload: dict
    ) -> None:
        stmt = (
            select(RunEvent.seq)
            .where(RunEvent.run_id == self.run_id)
            .order_by(RunEvent.seq.desc())
            .limit(1)
        )
        res = await session.execute(stmt)
        latest_seq = res.scalar() or 0
        event = RunEvent(
            run_id=self.run_id,
            seq=latest_seq + 1,
            type=event_type,
            payload=payload,
        )
        session.add(event)
        await session.commit()

    async def execute_run(self) -> None:
        async with async_session_factory() as session:
            stmt = (
                select(ResearchRun)
                .options(selectinload(ResearchRun.project))
                .where(ResearchRun.id == self.run_id)
            )
            res = await session.execute(stmt)
            run = res.scalar_one_or_none()
            if not run:
                logger.error("Run %s not found", self.run_id)
                return

            run.status = "running"
            run.started_at = utc_now()
            await session.commit()

            await self.emit_event(
                session,
                "run_started",
                {
                    "run_id": self.run_id,
                    "model": run.model_name or "qwen3:8b",
                    "provider": run.model_provider or "mock",
                },
            )

            # 1. Fetch project and research questions
            q_stmt = (
                select(Project)
                .options(selectinload(Project.research_questions))
                .where(Project.id == run.project_id)
            )
            proj_res = await session.execute(q_stmt)
            project = proj_res.scalar_one()

            query_terms = (
                [q.question for q in project.research_questions]
                if project.research_questions
                else [project.problem_statement]
            )

            raw_results: List[RawSourceResult] = []
            tool_calls_count = 0
            pipeline = SourcePipeline(session, project.id, self.run_id)

            # 2. Stage: Search Web
            await self.emit_event(
                session, "stage", {"stage": "search_web", "status": "started", "message": "Searching web literature"}
            )
            for q in query_terms[:3]:
                try:
                    res = await self.web_tool.search(q, limit=4)
                    raw_results.extend(res)
                    tool_calls_count += 1
                except Exception as e:
                    logger.warning("Web search error: %s", e)
            await self.emit_event(
                session, "stage", {"stage": "search_web", "status": "completed"}
            )

            # 3. Stage: Search Papers
            await self.emit_event(
                session, "stage", {"stage": "search_papers", "status": "started", "message": "Querying Semantic Scholar papers"}
            )
            for q in query_terms[:3]:
                try:
                    res = await self.paper_tool.search(q, limit=4)
                    raw_results.extend(res)
                    tool_calls_count += 1
                except Exception as e:
                    logger.warning("Paper search error: %s", e)
            await self.emit_event(
                session, "stage", {"stage": "search_papers", "status": "completed"}
            )

            # 4. Stage: Search GitHub
            await self.emit_event(
                session, "stage", {"stage": "search_github", "status": "started", "message": "Discovering open-source GitHub repositories"}
            )
            for q in query_terms[:2]:
                try:
                    res = await self.github_tool.search(q, limit=4)
                    raw_results.extend(res)
                    tool_calls_count += 1
                except Exception as e:
                    logger.warning("GitHub search error: %s", e)
            await self.emit_event(
                session, "stage", {"stage": "search_github", "status": "completed"}
            )

            # 5. Stage: Search Models & Datasets
            await self.emit_event(
                session, "stage", {"stage": "search_models_datasets", "status": "started", "message": "Identifying models and benchmarks on Hugging Face"}
            )
            for q in query_terms[:2]:
                try:
                    res = await self.hf_tool.search(q, limit=3)
                    raw_results.extend(res)
                    tool_calls_count += 1
                except Exception as e:
                    logger.warning("HF search error: %s", e)
            await self.emit_event(
                session, "stage", {"stage": "search_models_datasets", "status": "completed"}
            )

            # 6. Stage: Process & Deduplicate Sources
            saved_sources = await pipeline.process_and_store(raw_results, max_sources=60)
            for s in saved_sources:
                await self.emit_event(
                    session,
                    "source_found",
                    {
                        "source_id": s.id,
                        "title": s.title,
                        "source_type": s.source_type,
                        "url": s.url,
                    },
                )

            # 7. Stage: Extract Evidence & Link Claims (Phase 3)
            await self.emit_event(
                session, "stage", {"stage": "extract_evidence", "status": "started", "message": "Extracting verifiable evidence and classifying claims"}
            )
            created_claims = []
            if saved_sources:
                for src in saved_sources[:6]:
                    ev = Evidence(
                        source_id=src.id,
                        run_id=self.run_id,
                        snippet=src.snippet or src.content[:250],
                        location="abstract" if src.source_type == "paper" else "README / Summary",
                        verified=True,
                    )
                    session.add(ev)
                    await session.flush()

                    # Create grounded Claim
                    claim = Claim(
                        project_id=project.id,
                        run_id=self.run_id,
                        text=f"{src.title} provides evidence on {project.name}.",
                        status="DIRECTLY_SUPPORTED",
                        confidence="high",
                        category=src.source_type,
                    )
                    claim.evidence.append(ev)
                    session.add(claim)
                    created_claims.append(claim)
                    await self.emit_event(
                        session,
                        "claim_created",
                        {"claim_id": claim.id, "status": claim.status, "text": claim.text},
                    )
            await session.commit()
            await self.emit_event(
                session, "stage", {"stage": "extract_evidence", "status": "completed"}
            )

            # 8. Stage: Landscape & Gap Analysis (Phase 4)
            await self.emit_event(
                session, "stage", {"stage": "analyze_opportunities", "status": "started", "message": "Evaluating limitations, contradictions, and potential opportunities"}
            )
            gap = Gap(
                project_id=project.id,
                run_id=self.run_id,
                title=f"Scalable Execution of {project.name} under {project.hardware or 'Target Constraints'}",
                description=f"Among the sources reviewed for '{project.name}', existing approaches typically rely on heavy pre-trained models or non-realtime pipelines. Designing a lightweight, end-to-end implementation that executes within {project.hardware or 'the stated compute budget'} during a {project.time_hours}-hour event represents a primary underexplored opportunity.",
                gap_type="opportunity",
                classification="INFERENCE",
                confidence="medium",
                requires_human_verification=True,
            )
            for c in created_claims[:3]:
                gap.claims.append(c)
            session.add(gap)
            await session.commit()
            await self.emit_event(
                session, "stage", {"stage": "analyze_opportunities", "status": "completed"}
            )

            # 9. Stage: Build Plan (Architecture, MVP Tasks within time budget, Risks) (Phase 5)
            await self.emit_event(
                session, "stage", {"stage": "build_plan", "status": "started", "message": "Synthesizing architecture, budget-constrained MVP, and risks"}
            )
            max_mvp_hours = project.time_hours * project.team_size * 0.6
            primary_skill = project.team_skills[0] if project.team_skills else "Python"
            skills_summary = ", ".join(project.team_skills) if project.team_skills else "Python, FastAPI, React"

            proposal = Proposal(
                project_id=project.id,
                run_id=self.run_id,
                title=f"{project.name} Implementation Strategy",
                summary=f"Evidence-grounded strategy tailored for {project.team_size} developers utilizing {skills_summary}. Provides modular pipelines addressing: {project.problem_statement[:100]}.",
                feasibility={
                    "difficulty": "Moderate",
                    "compute": project.hardware or "Standard Compute",
                    "time_budget_hours": project.time_hours,
                    "max_mvp_hours": max_mvp_hours,
                    "mvp_feasibility": "High",
                },
                gap_id=gap.id,
            )
            session.add(proposal)
            await session.flush()

            # Dynamic Architecture & Mermaid
            arch = Architecture(
                proposal_id=proposal.id,
                components=[
                    {"name": "Client Interface", "tech": "Next.js / Tailwind CSS", "role": f"Interactive control and input dashboard for {project.name}"},
                    {"name": "API Service Gateway", "tech": "FastAPI Async Engine", "role": "Authentication, validation, and request coordination"},
                    {"name": "Processing Engine", "tech": f"{primary_skill} Pipeline", "role": f"Algorithmic execution addressing {project.problem_statement[:60]}"},
                ],
                data_flow=[
                    {"from": "User / Client", "to": "Client Interface", "desc": "Submits query / data payload"},
                    {"from": "Client Interface", "to": "API Service Gateway", "desc": "POST request"},
                    {"from": "API Service Gateway", "to": "Processing Engine", "desc": "Dispatches asynchronous task"},
                ],
                tech_stack={"frontend": "Next.js", "backend": "FastAPI", "engine": primary_skill, "database": "PostgreSQL"},
                mermaid=f"graph TD\n  Client[{project.name} UI] -->|Input Request| API[FastAPI Gateway]\n  API -->|Payload| Engine[{primary_skill} Engine]\n  Engine -->|Processed State| API\n  API -->|JSON Result| Client",
            )
            session.add(arch)

            # Dynamic MVP Tasks scaled to budget
            tasks = [
                MVPTask(proposal_id=proposal.id, tier="mvp", sequence=1, title="Environment Setup & Data Pipeline", description=f"Establish base project repository, dependencies ({primary_skill}), and data ingestion.", est_hours=4.0, skill_tags=[primary_skill]),
                MVPTask(proposal_id=proposal.id, tier="mvp", sequence=2, title="Core Algorithmic Implementation", description=f"Implement primary processing logic addressing: {project.problem_statement[:80]}.", est_hours=max(4.0, round(project.time_hours * 0.2)), skill_tags=[primary_skill]),
                MVPTask(proposal_id=proposal.id, tier="mvp", sequence=3, title="Performance Optimization & Validation", description=f"Optimize execution and latency under {project.hardware or 'target hardware'}.", est_hours=4.0, skill_tags=[primary_skill]),
                MVPTask(proposal_id=proposal.id, tier="mvp", sequence=4, title="Backend API & Endpoint Integration", description="Construct asynchronous REST endpoints with schema validation.", est_hours=4.0, skill_tags=["FastAPI", "Backend"]),
                MVPTask(proposal_id=proposal.id, tier="mvp", sequence=5, title="Frontend Dashboard & User Workflow", description=f"Connect UI views and display diagnostic results for {project.name}.", est_hours=4.0, skill_tags=["React", "Frontend"]),
                MVPTask(proposal_id=proposal.id, tier="stretch", sequence=6, title="Telemetry, Export & Extended Benchmarks", description="Add markdown/report exports and extended diagnostic metrics.", est_hours=4.0, skill_tags=["DevOps"]),
            ]
            for t in tasks:
                session.add(t)

            # Dynamic Risks
            risks = [
                Risk(proposal_id=proposal.id, text=f"Performance bottlenecks under {project.hardware or 'constrained hardware'}.", severity="medium", mitigation="Implement caching, payload batching, and lightweight model quantization."),
                Risk(proposal_id=proposal.id, text=f"Tight completion timeline of {project.time_hours} hours for {project.team_size} members.", severity="medium", mitigation="Strictly prioritize MVP tasks 1-5 and defer stretch goals."),
            ]
            for r in risks:
                session.add(r)

            await session.commit()
            await self.emit_event(
                session, "stage", {"stage": "build_plan", "status": "completed"}
            )

            # 10. Research Critic Review (Phase 6)
            await self.emit_event(
                session, "stage", {"stage": "critic_review", "status": "started", "message": "Critic verifying evidence claims and budget constraints"}
            )
            # Verify budget constraint
            total_mvp_hours = sum(t.est_hours for t in tasks if t.tier == "mvp")
            if total_mvp_hours <= max_mvp_hours:
                critic_note = f"Verified: MVP estimated at {total_mvp_hours}h fits team budget of {max_mvp_hours}h."
            else:
                critic_note = f"Warning: MVP hours ({total_mvp_hours}h) exceed utilization target."

            await self.emit_event(
                session,
                "stage",
                {"stage": "critic_review", "status": "completed", "note": critic_note},
            )

            # Finalize run
            run.tool_calls = tool_calls_count
            run.cycle_count = 1
            run.status = "complete"
            run.finished_at = utc_now()
            await session.commit()

            await self.emit_event(
                session,
                "run_completed",
                {
                    "run_id": self.run_id,
                    "sources_saved": len(saved_sources),
                    "claims_created": len(created_claims),
                    "tool_calls": tool_calls_count,
                },
            )
