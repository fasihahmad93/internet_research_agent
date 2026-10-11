"""HTTP routes."""

from fastapi import APIRouter, Depends

from research_agent.api.dependencies import get_research_service
from research_agent.api.errors import ResearchError
from research_agent.api.schemas import (
    HealthResponse,
    ResearchRequest,
    ResearchResponse,
)
from research_agent.observability.logging_config import log_function
from research_agent.services.research_service import ResearchRunner

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
@log_function
def health_check() -> HealthResponse:
    """Report whether the API process is responsive."""
    return HealthResponse(status="ok")


@router.post(
    "/research",
    response_model=ResearchResponse,
    tags=["research"],
    summary="Research a question",
)
@log_function
def create_research(
    request: ResearchRequest,
    service: ResearchRunner = Depends(get_research_service),
) -> ResearchResponse:
    """Search the web and return a source-backed report."""
    try:
        report = service.research(request)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ResearchError(str(exc)) from exc
    return ResearchResponse(report=report)
