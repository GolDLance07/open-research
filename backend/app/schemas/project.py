from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    competition_name: Optional[str] = Field(default=None, max_length=255)
    problem_statement: str = Field(..., min_length=20, max_length=20000)
    rules_text: Optional[str] = Field(default=None, max_length=20000)
    judging_text: Optional[str] = Field(default=None, max_length=20000)
    team_size: int = Field(default=1, ge=1, le=20)
    team_skills: List[str] = Field(default_factory=list, max_length=20)
    time_hours: int = Field(default=24, ge=1, le=720)
    hardware: Optional[str] = Field(default=None, max_length=255)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    competition_name: Optional[str] = Field(default=None, max_length=255)
    problem_statement: Optional[str] = Field(default=None, min_length=20, max_length=20000)
    rules_text: Optional[str] = Field(default=None, max_length=20000)
    judging_text: Optional[str] = Field(default=None, max_length=20000)
    team_size: Optional[int] = Field(default=None, ge=1, le=20)
    team_skills: Optional[List[str]] = Field(default=None, max_length=20)
    time_hours: Optional[int] = Field(default=None, ge=1, le=720)
    hardware: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    competition_name: Optional[str] = None
    problem_statement: str
    rules_text: Optional[str] = None
    judging_text: Optional[str] = None
    team_size: int
    team_skills: List[str]
    time_hours: int
    hardware: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
