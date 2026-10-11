"""HTTP routes."""

from fastapi import APIRouter

from research_agent.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Report whether the API process is responsive."""
    return HealthResponse(status="ok")
