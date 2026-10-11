"""Shared API dependency providers."""

from fastapi import Request

from research_agent.services.research_service import ResearchRunner


def get_research_service(request: Request) -> ResearchRunner:
    """Resolve the application-level research service."""
    service = getattr(request.app.state, "research_service", None)
    if service is None:
        raise RuntimeError("Research service is not configured")
    return service
