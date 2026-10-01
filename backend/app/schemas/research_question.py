from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

PriorityType = Literal["high", "medium", "low"]


class ResearchQuestionItem(BaseModel):
    id: Optional[str] = None  # e.g. 'RQ1'
    question: str = Field(..., min_length=10)
    priority: PriorityType = "medium"
    coverage_area: Optional[str] = None


class ResearchPlannerOutput(BaseModel):
    questions: List[ResearchQuestionItem] = Field(default_factory=list)


class ResearchQuestionResponse(BaseModel):
    id: str
    project_id: str
    label: str
    question: str
    priority: str
    status: str
    position: int = 0

    model_config = ConfigDict(from_attributes=True)


class ResearchQuestionUpdate(BaseModel):
    question: Optional[str] = Field(default=None, min_length=5)
    priority: Optional[PriorityType] = None
    status: Optional[str] = None
    position: Optional[int] = None
