"""Evidence domain models."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class SearchHit(BaseModel):
    """A search-engine result before fetching the source page."""

    title: str
    url: str
    snippet: str = ""


class EvidenceItem(BaseModel):
    """A fetched source with its excerpt, source URL, and discovered links."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    url: str
    snippet: str = ""
    content: str
    links: list[str] = Field(default_factory=list)
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ResearchEvidence(BaseModel):
    """Collection of sources gathered for a research request."""

    items: list[EvidenceItem] = Field(default_factory=list)
