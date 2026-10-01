from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

RequirementKind = Literal["requirement", "constraint", "deliverable", "judging_criterion"]


class RequirementItem(BaseModel):
    text: str = Field(..., min_length=3)
    source_span: Optional[str] = None
    priority: Optional[str] = Field(default="medium")
    severity: Optional[str] = Field(default="info")  # For constraints: warning, critical, info


class RequirementAnalysisOutput(BaseModel):
    requirements: List[RequirementItem] = Field(default_factory=list)
    constraints: List[RequirementItem] = Field(default_factory=list)
    deliverables: List[RequirementItem] = Field(default_factory=list)
    judging_criteria: List[RequirementItem] = Field(default_factory=list)


class RequirementResponse(BaseModel):
    id: str
    project_id: str
    kind: RequirementKind
    text: str
    source_span: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    user_edited: bool = False
    position: int = 0

    model_config = ConfigDict(from_attributes=True)


class RequirementUpdate(BaseModel):
    text: Optional[str] = Field(default=None, min_length=1)
    priority: Optional[str] = None
    severity: Optional[str] = None
    position: Optional[int] = None
