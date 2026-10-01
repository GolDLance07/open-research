from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResearchRunRequest(BaseModel):
    max_cycles: int = Field(default=2, ge=1, le=5)
    include: List[Literal["web", "papers", "github", "models", "datasets"]] = Field(
        default_factory=lambda: ["web", "papers", "github", "models", "datasets"]
    )


class ResearchRunResponse(BaseModel):
    run_id: str
    status: str
    stream_url: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    tool_calls: int = 0
    cycle_count: int = 0
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SourceResponse(BaseModel):
    id: str
    project_id: str
    run_id: Optional[str] = None
    title: str
    url: str
    canonical_url: str
    source_type: str
    author: Optional[str] = None
    published_date: Optional[date] = None
    publisher: Optional[str] = None
    snippet: str
    retrieved_at: datetime
    license: Optional[str] = None
    relevance_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaperResponse(BaseModel):
    source_id: str
    external_id: Optional[str] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    citation_count: Optional[int] = None
    abstract: Optional[str] = None
    authors: List[str] = []
    open_access_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RepositoryResponse(BaseModel):
    source_id: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    license: Optional[str] = None
    topics: List[str] = []
    readme_summary: Optional[str] = None
    archived: bool = False

    model_config = ConfigDict(from_attributes=True)


class ModelEntityResponse(BaseModel):
    source_id: str
    hub_id: str
    task: Optional[str] = None
    license: Optional[str] = None
    params: Optional[str] = None
    downloads: int = 0
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetEntityResponse(BaseModel):
    source_id: str
    hub_id: str
    license: Optional[str] = None
    size_note: Optional[str] = None
    modality: Optional[str] = None
    access_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
