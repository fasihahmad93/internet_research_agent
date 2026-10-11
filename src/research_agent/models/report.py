"""Research report domain models."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from research_agent.models.evidence import EvidenceItem


class ReportFinding(BaseModel):
    """A report claim and the evidence identifiers supporting it."""

    text: str
    evidence_ids: list[UUID] = Field(default_factory=list)


class ReportDraft(BaseModel):
    """Structured model output before source metadata is attached."""

    title: str
    summary: str
    findings: list[ReportFinding] = Field(default_factory=list)


class ResearchReport(BaseModel):
    """Final report returned to the API caller."""

    id: UUID = Field(default_factory=uuid4)
    query: str
    title: str
    summary: str
    findings: list[ReportFinding]
    citations: list[EvidenceItem]
    quality_score: float = Field(ge=0, le=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
