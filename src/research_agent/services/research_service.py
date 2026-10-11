"""Research orchestration service."""

import logging
from typing import Protocol

from research_agent.agent.graph import ResearchGraph
from research_agent.models.research import ResearchRequest
from research_agent.models.report import ResearchReport
from research_agent.observability.events import emit_event
from research_agent.observability.metrics import increment
from research_agent.storage.repositories import ReportRepository

logger = logging.getLogger(__name__)


class ResearchRunner(Protocol):
    """Structural interface accepted by API handlers and test doubles."""

    def research(self, request: ResearchRequest) -> ResearchReport: ...


class ResearchService:
    """Application-facing research workflow."""

    def __init__(
        self, graph: ResearchGraph, repository: ReportRepository | None = None
    ) -> None:
        self._graph = graph
        self._repository = repository

    def research(self, request: ResearchRequest) -> ResearchReport:
        """Run a research request and return its evidence-backed report."""
        increment("research.started")
        emit_event(
            "research.started",
            depth=request.depth.value,
            query_length=len(request.query),
        )
        try:
            report = self._graph.run(request)
            if self._repository is not None:
                self._repository.save(report)
        except (OSError, RuntimeError, ValueError):
            increment("research.failed")
            logger.exception("Research request failed")
            emit_event("research.failed", depth=request.depth.value)
            raise
        increment("research.completed")
        emit_event(
            "research.completed",
            evidence_count=len(report.citations),
            quality_score=report.quality_score,
        )
        return report
