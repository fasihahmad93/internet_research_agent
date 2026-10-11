"""API error types and exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ResearchError(RuntimeError):
    """A known failure while running a research request."""


def register_error_handlers(app: FastAPI) -> None:
    """Register stable JSON responses for expected research failures."""

    @app.exception_handler(ResearchError)
    async def research_error_handler(
        request: Request, exc: ResearchError
    ) -> JSONResponse:
        del request
        return JSONResponse(status_code=502, content={"detail": str(exc)})
