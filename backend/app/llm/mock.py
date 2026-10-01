import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from app.llm.base import LLMMessage, LLMOutputError, LLMProvider, LLMResult

T = TypeVar("T", bound=BaseModel)


DEFAULT_MOCK_RESPONSES: Dict[str, Any] = {
    "RequirementAnalysisOutput": {
        "requirements": [
            {
                "text": "Early detection and classification of crop pathology using vision models",
                "source_span": "Build an AI system for early detection of crop diseases",
                "priority": "high",
            },
            {
                "text": "Support inference in low-resource and edge environments",
                "source_span": "low-resource environments",
                "priority": "high",
            },
        ],
        "constraints": [
            {
                "text": "Project must fit within the 36-hour team time budget",
                "source_span": "36 hours",
                "severity": "warning",
            },
            {
                "text": "Compute constrained to single GPU / edge hardware",
                "source_span": "Limited GPU",
                "severity": "warning",
            },
            {
                "text": "All code and deliverables must be released under an OSI-approved open source license",
                "source_span": "open source",
                "severity": "info",
            },
        ],
        "deliverables": [
            {
                "text": "Working repository with documented installation and model inference scripts",
                "source_span": None,
            },
            {
                "text": "Evidence-backed architecture document and MVP demo",
                "source_span": None,
            },
        ],
        "judging_criteria": [
            {
                "text": "Technical depth and demonstrable feasibility within stated constraints",
                "source_span": "judging criteria",
            },
            {
                "text": "Evidence traceability from academic papers and open-source models",
                "source_span": None,
            },
        ],
    },
    "ResearchPlannerOutput": {
        "questions": [
            {
                "id": "RQ1",
                "question": "What are the established lightweight computer vision architectures (CNNs, MobileNets, ViTs) for crop disease classification?",
                "priority": "high",
                "coverage_area": "existing_approaches",
            },
            {
                "id": "RQ2",
                "question": "What open benchmark datasets (e.g. PlantVillage, Cassava) are available with permissive licenses?",
                "priority": "high",
                "coverage_area": "datasets_and_benchmarks",
            },
            {
                "id": "RQ3",
                "question": "What open-source repositories provide battle-tested pretrained weights for plant leaf pathology?",
                "priority": "medium",
                "coverage_area": "open_source_repos",
            },
            {
                "id": "RQ4",
                "question": "What model quantization techniques (ONNX, TensorRT, INT8) best fit the team's hardware and latency constraints?",
                "priority": "medium",
                "coverage_area": "feasibility_and_tradeoffs",
            },
            {
                "id": "RQ5",
                "question": "What limitations in field-generalization and lighting robustness present viable differentiation opportunities?",
                "priority": "high",
                "coverage_area": "potential_gaps",
            },
        ]
    },
}


class MockProvider(LLMProvider):
    name: str = "mock"
    model: str = "qwen3:8b-mock"

    def __init__(self, canned_responses: Optional[Dict[str, Any]] = None):
        merged = dict(DEFAULT_MOCK_RESPONSES)
        if canned_responses:
            merged.update(canned_responses)
        self.canned_responses = merged

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

        # Deterministic mock response
        response_text = f"[Mock Qwen3-8B Response] Received {len(messages)} messages. Last prompt: {user_prompt[:80]}"
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
        if schema_name in self.canned_responses:
            data = self.canned_responses[schema_name]
            return schema.model_validate(data)

        # Generate a minimal valid dummy instance for any Pydantic schema
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
