from pathlib import Path
from typing import List, Optional
from app.db.models.project import Project
from app.llm.base import LLMMessage, LLMProvider
from app.schemas.requirement import RequirementAnalysisOutput
from app.schemas.research_question import ResearchPlannerOutput


def load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent / "llm" / "prompts" / "research_planner.md"
    )
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "Generate prioritized research questions covering existing approaches, datasets, repos, feasibility, and gaps."


class ResearchPlanner:
    name: str = "ResearchPlanner"

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.system_prompt = load_prompt()

    async def run(
        self,
        project: Project,
        requirements_output: Optional[RequirementAnalysisOutput] = None,
    ) -> ResearchPlannerOutput:
        req_summary = ""
        if requirements_output:
            req_summary = (
                f"Requirements: {len(requirements_output.requirements)}\n"
                f"Constraints: {len(requirements_output.constraints)}\n"
                f"Deliverables: {len(requirements_output.deliverables)}\n"
            )

        user_content = (
            f"Project: {project.name}\n"
            f"Problem: {project.problem_statement}\n"
            f"Team Profile: {project.team_size} members with skills: {', '.join(project.team_skills or [])}\n"
            f"Time Budget: {project.time_hours} hours\n"
            f"Hardware: {project.hardware or 'General'}\n"
            f"{req_summary}\n"
            f"Please generate 5-10 prioritized research questions (RQ1, RQ2, ...) to guide technical research."
        )

        messages = [
            LLMMessage(role="system", content=self.system_prompt),
            LLMMessage(role="user", content=user_content),
        ]

        result = await self.llm.structured(
            messages,
            ResearchPlannerOutput,
            temperature=0.5,
            thinking=True,
        )

        # Ensure labels are populated
        for i, q in enumerate(result.questions, start=1):
            if not q.id or not q.id.startswith("RQ"):
                q.id = f"RQ{i}"

        return result
