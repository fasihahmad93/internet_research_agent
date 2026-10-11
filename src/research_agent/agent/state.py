"""Shared state types for the research graph."""

from dataclasses import dataclass, field

from research_agent.models.evidence import EvidenceItem, SearchHit
from research_agent.models.research import ResearchRequest
from research_agent.models.report import ResearchReport


@dataclass
class ResearchState:
    """Mutable context passed between research graph nodes."""

    request: ResearchRequest
    search_hits: list[SearchHit] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    report: ResearchReport | None = None
