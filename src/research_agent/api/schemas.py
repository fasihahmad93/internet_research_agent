"""API request and response schemas."""

from pydantic import BaseModel

from research_agent.models.report import ResearchReport
from research_agent.models.research import ResearchRequest


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str


class ResearchResponse(BaseModel):
    """Response containing a generated research report."""

    report: ResearchReport


__all__ = ["HealthResponse", "ResearchRequest", "ResearchResponse"]
