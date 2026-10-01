import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_db
from app.config import get_settings
from app.db.models.analysis import (
    Architecture,
    Claim,
    Evidence,
    Gap,
    IdeaChallenge,
    MVPTask,
    Proposal,
    Risk,
)
from app.db.models.project import Project
from app.db.models.research_run import ResearchRun, RunEvent
from app.db.models.source import DatasetEntity, ModelEntity, Paper, Repository, Source
from app.orchestrator.runner import ResearchOrchestrator
from app.schemas.research_run import (
    DatasetEntityResponse,
    ModelEntityResponse,
    PaperResponse,
    RepositoryResponse,
    ResearchRunRequest,
    ResearchRunResponse,
    SourceResponse,
)

router = APIRouter()
settings = get_settings()


@router.post(
    "/projects/{id}/research",
    response_model=ResearchRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_research_run(
    id: str,
    body: Optional[ResearchRunRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
) -> ResearchRunResponse:
    if body is None:
        body = ResearchRunRequest()
    stmt = select(Project).where(Project.id == id)
    res = await db.execute(stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{id}' not found",
        )

    # Check active run
    active_stmt = select(ResearchRun).where(
        ResearchRun.project_id == id,
        ResearchRun.status.in_(["queued", "running"]),
    )
    active_res = await db.execute(active_stmt)
    if active_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A research run is already active for this project.",
        )

    run = ResearchRun(
        project_id=id,
        kind="research",
        status="queued",
        model_provider=settings.LLM_PROVIDER,
        model_name=settings.MODEL_NAME,
        budget={
            "max_cycles": body.max_cycles,
            "max_tool_calls": settings.MAX_TOOL_CALLS,
            "max_sources": settings.MAX_SOURCES,
        },
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    orchestrator = ResearchOrchestrator(run.id)
    background_tasks.add_task(orchestrator.execute_run)

    return ResearchRunResponse(
        run_id=run.id,
        status="queued",
        stream_url=f"/api/v1/research/{run.id}/stream",
        started_at=run.started_at,
        finished_at=run.finished_at,
        tool_calls=run.tool_calls,
        cycle_count=run.cycle_count,
    )


@router.get("/projects/{id}/research/{run_id}", response_model=ResearchRunResponse)
async def get_research_run(
    id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResearchRunResponse:
    stmt = select(ResearchRun).where(
        ResearchRun.id == run_id, ResearchRun.project_id == id
    )
    res = await db.execute(stmt)
    run = res.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research run '{run_id}' not found for project '{id}'",
        )
    return ResearchRunResponse(
        run_id=run.id,
        status=run.status,
        stream_url=f"/api/v1/research/{run.id}/stream",
        started_at=run.started_at,
        finished_at=run.finished_at,
        tool_calls=run.tool_calls,
        cycle_count=run.cycle_count,
        error=run.error,
    )


@router.get("/research/{run_id}/stream")
async def stream_run_events(
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        last_seq = 0
        attempts = 0
        while attempts < 120:
            stmt = (
                select(RunEvent)
                .where(RunEvent.run_id == run_id, RunEvent.seq > last_seq)
                .order_by(RunEvent.seq.asc())
            )
            res = await db.execute(stmt)
            events = res.scalars().all()

            for event in events:
                last_seq = event.seq
                data_json = json.dumps(
                    {"type": event.type, "payload": event.payload, "seq": event.seq}
                )
                yield f"id: {event.seq}\nevent: {event.type}\ndata: {data_json}\n\n"

                if event.type in ("run_completed", "run_failed"):
                    return

            await asyncio.sleep(0.5)
            attempts += 1

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/projects/{id}/sources", response_model=List[SourceResponse])
async def list_sources(
    id: str,
    source_type: Optional[str] = Query(None, alias="type"),
    run_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[SourceResponse]:
    stmt = select(Source).where(Source.project_id == id)
    if source_type:
        stmt = stmt.where(Source.source_type == source_type)
    if run_id:
        stmt = stmt.where(Source.run_id == run_id)
    stmt = stmt.order_by(Source.retrieved_at.desc())

    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/projects/{id}/claims")
async def list_claims(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    stmt = (
        select(Claim)
        .options(selectinload(Claim.evidence).selectinload(Evidence.source))
        .where(Claim.project_id == id)
    )
    res = await db.execute(stmt)
    claims = res.scalars().all()

    output = []
    for c in claims:
        ev_list = []
        for e in c.evidence:
            ev_list.append({
                "id": e.id,
                "snippet": e.snippet,
                "location": e.location,
                "verified": e.verified,
                "source": {
                    "id": e.source.id,
                    "title": e.source.title,
                    "url": e.source.url,
                    "source_type": e.source.source_type,
                } if e.source else None,
            })
        output.append({
            "id": c.id,
            "text": c.text,
            "status": c.status,
            "confidence": c.confidence,
            "category": c.category,
            "critic_flags": c.critic_flags,
            "reasoning": c.reasoning,
            "evidence": ev_list,
        })
    return output


@router.get("/projects/{id}/gaps")
async def list_gaps(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    stmt = select(Gap).options(selectinload(Gap.claims)).where(Gap.project_id == id)
    res = await db.execute(stmt)
    gaps = res.scalars().all()

    output = []
    for g in gaps:
        output.append({
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "gap_type": g.gap_type,
            "classification": g.classification,
            "confidence": g.confidence,
            "requires_human_verification": g.requires_human_verification,
            "claims_count": len(g.claims),
            "claim_ids": [c.id for c in g.claims],
        })
    return output


@router.get("/projects/{id}/build-plan")
async def get_build_plan(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    stmt = (
        select(Proposal)
        .options(
            selectinload(Proposal.architecture),
            selectinload(Proposal.mvp_tasks),
            selectinload(Proposal.risks),
        )
        .where(Proposal.project_id == id)
        .order_by(Proposal.id.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    proposal = res.scalar_one_or_none()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Build plan not found for project '{id}'. Run research first.",
        )

    return {
        "id": proposal.id,
        "title": proposal.title,
        "summary": proposal.summary,
        "feasibility": proposal.feasibility,
        "architecture": {
            "components": proposal.architecture.components if proposal.architecture else [],
            "data_flow": proposal.architecture.data_flow if proposal.architecture else [],
            "tech_stack": proposal.architecture.tech_stack if proposal.architecture else {},
            "mermaid": proposal.architecture.mermaid if proposal.architecture else "",
        } if proposal.architecture else None,
        "tasks": [
            {
                "id": t.id,
                "tier": t.tier,
                "sequence": t.sequence,
                "title": t.title,
                "description": t.description,
                "est_hours": t.est_hours,
                "skill_tags": t.skill_tags,
            }
            for t in proposal.mvp_tasks
        ],
        "risks": [
            {
                "id": r.id,
                "text": r.text,
                "severity": r.severity,
                "mitigation": r.mitigation,
            }
            for r in proposal.risks
        ],
    }


@router.post("/projects/{id}/challenge-idea")
async def challenge_idea(
    id: str,
    idea_payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    idea_text = idea_payload.get("idea_text", "")
    if len(idea_text) < 10:
        raise HTTPException(status_code=422, detail="Idea text must be at least 10 characters")

    # Retrieve project and existing sources for context
    p_stmt = select(Project).where(Project.id == id)
    p_res = await db.execute(p_stmt)
    proj = p_res.scalar_one_or_none()
    proj_name = proj.name if proj else "Project"

    s_stmt = select(Source).where(Source.project_id == id).limit(5)
    s_res = await db.execute(s_stmt)
    sources = s_res.scalars().all()

    challenge = IdeaChallenge(
        project_id=id,
        idea_text=idea_text,
        related_work={
            "count": len(sources),
            "sources": [{"title": s.title, "url": s.url, "type": s.source_type} for s in sources],
        },
        issues=[
            {
                "type": "Generalization / Real-world Distribution Shift",
                "detail": f"Real-world edge cases and noisy inputs for '{idea_text[:60]}' frequently degrade baseline performance reported in academic benchmarks.",
            },
            {
                "type": "Resource & Hardware Constraints",
                "detail": f"Execution profile must be profiled carefully to avoid violating runtime and memory limits on {proj.hardware if proj else 'target compute'}.",
            },
        ],
        differentiation={
            "same_as_existing": [
                f"Standard baseline techniques identified in related literature for {proj_name}",
                "Conventional unoptimized processing pipelines",
            ],
            "differentiation_angles": [
                f"Novel combination addressing specific constraints: {idea_text[:80]}",
                "Streamlined architecture optimized for deterministic fast turnaround",
            ],
        },
        suggested_investigation=[
            f"Benchmark {proj_name} under adversarial or noisy input conditions.",
            "Profile latency bottlenecks on target deployment hardware before freezing MVP scope.",
        ],
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)

    return {
        "id": challenge.id,
        "idea_text": challenge.idea_text,
        "related_work": challenge.related_work,
        "issues": challenge.issues,
        "differentiation": challenge.differentiation,
        "suggested_investigation": challenge.suggested_investigation,
    }


@router.get("/projects/{id}/report.md")
async def export_report_markdown(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    p_stmt = (
        select(Project)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.research_questions),
            selectinload(Project.sources),
        )
        .where(Project.id == id)
    )
    res = await db.execute(p_stmt)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    md = f"""# Research & Build Strategy Report: {project.name}

## 1. Problem Statement
{project.problem_statement}

## 2. Requirements & Constraints
"""
    for r in project.requirements:
        md += f"- **[{r.kind.upper()}]** {r.text} *(Priority: {r.priority or 'N/A'})*\n"

    md += "\n## 3. Researched Sources & Evidence\n"
    for s in project.sources:
        md += f"- **[{s.source_type.upper()}]** [{s.title}]({s.url}) — {s.snippet[:150]}...\n"

    md += "\n---\n*Generated by OpenResearch powered by open-weight reasoning.*"
    return Response(content=md, media_type="text/markdown")
