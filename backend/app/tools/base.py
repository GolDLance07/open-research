from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

SourceType = Literal["web", "paper", "repository", "model", "dataset"]


class RawSourceResult(BaseModel):
    title: str
    url: str
    source_type: SourceType
    author: Optional[str] = None
    published_date: Optional[date] = None
    publisher: Optional[str] = None
    content: str = ""
    snippet: str = ""
    license: Optional[str] = None
    relevance_note: Optional[str] = None
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class Tool(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[RawSourceResult]:
        pass
