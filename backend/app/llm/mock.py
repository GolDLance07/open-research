import re
import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from app.llm.base import LLMMessage, LLMOutputError, LLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


def extract_field_from_prompt(prompt: str, field_name: str, default: str = "") -> str:
    """Extract field value from structured prompt text."""
    pattern = rf"{field_name}:\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)"
    match = re.search(pattern, prompt, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return default


def generate_dynamic_mock_data(prompt: str, schema_name: str) -> Dict[str, Any]:
    """Dynamically generate realistic structured output tailored to ANY user prompt."""
    name = (
        extract_field_from_prompt(prompt, "Project Name")
        or extract_field_from_prompt(prompt, "Project")
        or "Technical Project"
    )
    problem = (
        extract_field_from_prompt(prompt, "Problem Statement")
        or extract_field_from_prompt(prompt, "Problem")
        or "Build an innovative AI and software engineering solution"
    )
    # Clean problem summary
    problem_summary = problem.split("\n")[0][:120].strip()
    if not problem_summary.endswith("."):
        problem_summary += "."

    rules = extract_field_from_prompt(prompt, "Rules", "Standard open source submission rules")
    time_hours = extract_field_from_prompt(prompt, "Time Budget", "36")
    time_num = "".join(ch for ch in time_hours if ch.isdigit()) or "36"
    hardware = extract_field_from_prompt(prompt, "Hardware", "Standard compute")
    skills = extract_field_from_prompt(prompt, "Skills", "Python, React, Machine Learning")

    if schema_name == "RequirementAnalysisOutput":
        return {
            "requirements": [
                {
                    "text": f"Core System: Implement automated solution addressing: {problem_summary}",
                    "source_span": problem[:80],
                    "priority": "high",
                },
                {
                    "text": f"Performance & Runtime: Ensure efficient execution within {hardware} compute constraints",
                    "source_span": hardware[:60] if hardware != "Standard compute" else None,
                    "priority": "high",
                },
                {
                    "text": f"Interoperability: Provide clear integration interfaces utilizing {skills}",
                    "source_span": None,
                    "priority": "medium",
                },
            ],
            "constraints": [
                {
                    "text": f"Time Limitation: Complete MVP development within {time_num} hours",
                    "source_span": f"{time_num} hours",
                    "severity": "warning",
                },
                {
                    "text": f"Hardware Constraint: Execution target is {hardware}",
                    "source_span": hardware[:60],
                    "severity": "warning",
                },
                {
                    "text": f"Project Rules: {rules}",
                    "source_span": rules[:80] if rules != "Standard open source submission rules" else None,
                    "severity": "info",
                },
            ],
            "deliverables": [
                {
                    "text": f"Working repository with source code, setup guide, and tests for {name}",
                    "source_span": None,
                },
                {
                    "text": f"Evidence-backed architecture document and MVP demo showcasing {problem_summary}",
                    "source_span": None,
                },
            ],
            "judging_criteria": [
                {
                    "text": f"Technical depth, execution quality, and feasibility of {name}",
                    "source_span": None,
                },
                {
                    "text": "Evidence provenance and citation of established models and papers",
                    "source_span": None,
                },
            ],
        }

    elif schema_name == "ResearchPlannerOutput":
        return {
            "questions": [
                {
                    "id": "RQ1",
                    "question": f"What are the established baseline architectures and algorithmic models for {problem_summary}?",
                    "priority": "high",
                    "coverage_area": "existing_approaches",
                },
                {
                    "id": "RQ2",
                    "question": f"What public datasets, benchmarks, or validation corpora are available for {name}?",
                    "priority": "high",
                    "coverage_area": "datasets_and_benchmarks",
                },
                {
                    "id": "RQ3",
                    "question": f"What open-source repositories provide battle-tested implementations or weights for {name}?",
                    "priority": "medium",
                    "coverage_area": "open_source_repos",
                },
                {
                    "id": "RQ4",
                    "question": f"What optimization techniques best balance accuracy and latency under {hardware} within {time_num}h?",
                    "priority": "medium",
                    "coverage_area": "feasibility_and_tradeoffs",
                },
                {
                    "id": "RQ5",
                    "question": f"What limitations or underexplored areas in existing {name} solutions offer the strongest opportunity for differentiation?",
                    "priority": "high",
                    "coverage_area": "potential_gaps",
                },
            ]
        }

    return {}


class MockProvider(LLMProvider):
    name: str = "mock"
    model: str = "qwen3:8b-mock"

    def __init__(self, canned_responses: Optional[Dict[str, Any]] = None):
        self.canned_responses = canned_responses or {}

    async def chat(
        self,
        messages: List[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        thinking: bool = False,
        timeout_s: float = 120.0,
    ) -> LLMResult:
        start_time = time.perf_counter()
        user_prompt = messages[-1].content if messages else ""

        response_text = f"[Mock Qwen3-8B Response] Received prompt: {user_prompt[:100]}"
        latency_ms = (time.perf_counter() - start_time) * 1000

        return LLMResult(
            text=response_text,
            prompt_tokens=len(user_prompt.split()),
            completion_tokens=len(response_text.split()),
            latency_ms=round(latency_ms, 2),
        )

    async def structured(
        self,
        messages: List[LLMMessage],
        schema: Type[T],
        *,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        thinking: bool = False,
        repair_attempts: int = 1,
    ) -> T:
        schema_name = schema.__name__
        user_prompt = "\n".join(m.content for m in messages)

        # 1. Custom canned responses take priority if set in unit test
        if schema_name in self.canned_responses:
            data = self.canned_responses[schema_name]
            return schema.model_validate(data)

        # 2. Dynamically generate schema data tailored to the exact user prompt
        dynamic_data = generate_dynamic_mock_data(user_prompt, schema_name)
        if dynamic_data:
            return schema.model_validate(dynamic_data)

        # 3. Fallback dummy structure
        dummy_data: Dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            origin = getattr(annotation, "__origin__", None)

            if origin in (list, List):
                dummy_data[field_name] = []
            elif origin in (dict, Dict):
                dummy_data[field_name] = {}
            elif annotation in (int, float):
                dummy_data[field_name] = 0
            elif annotation is bool:
                dummy_data[field_name] = True
            elif annotation is str:
                dummy_data[field_name] = f"Mock {field_name}"
            elif hasattr(annotation, "model_fields"):
                dummy_data[field_name] = {}
            else:
                dummy_data[field_name] = None

        try:
            return schema.model_validate(dummy_data)
        except Exception as e:
            raise LLMOutputError(
                f"Failed to generate mock structured output for {schema_name}: {e}",
                raw_output=str(dummy_data),
            )

    async def health(self) -> bool:
        return True
