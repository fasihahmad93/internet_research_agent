"""API error types and exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from research_agent.observability.logging_config import log_function


class ResearchError(RuntimeError):
    """A known failure while running a research request."""


@log_function
def register_error_handlers(app: FastAPI) -> None:
    """Register stable JSON responses for expected research failures."""

    @app.exception_handler(ResearchError)
    @log_function
    async def research_error_handler(
        request: Request, exc: ResearchError
    ) -> JSONResponse:
        del request
        return JSONResponse(status_code=502, content={"detail": str(exc)})
