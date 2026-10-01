import os
from pathlib import Path
from app.db.models.project import Project
from app.llm.base import LLMMessage, LLMProvider
from app.schemas.requirement import RequirementAnalysisOutput


def load_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent / "llm" / "prompts" / "requirement_analyzer.md"
    )
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "Extract structured requirements, constraints, deliverables, and judging criteria."


class RequirementAnalyzer:
    name: str = "RequirementAnalyzer"

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.system_prompt = load_prompt()

    async def run(self, project: Project) -> RequirementAnalysisOutput:
        user_content = (
            f"Project Name: {project.name}\n"
            f"Problem Statement:\n{project.problem_statement}\n\n"
            f"Competition / Brief Rules:\n{project.rules_text or 'None specified'}\n\n"
            f"Judging Criteria:\n{project.judging_text or 'None specified'}\n\n"
            f"Team Profile: Size {project.team_size}, Skills: {', '.join(project.team_skills or [])}\n"
            f"Time Budget: {project.time_hours} hours\n"
            f"Hardware / Compute: {project.hardware or 'Standard compute'}\n"
        )

        messages = [
            LLMMessage(role="system", content=self.system_prompt),
            LLMMessage(role="user", content=user_content),
        ]

        return await self.llm.structured(
            messages,
            RequirementAnalysisOutput,
            temperature=0.1,
            thinking=False,
        )
