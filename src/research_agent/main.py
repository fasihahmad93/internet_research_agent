"""Application entry point."""

import logging

import uvicorn
from fastapi import FastAPI

from research_agent.api.errors import register_error_handlers
from research_agent.api.routes import router
from research_agent.config import Settings
from research_agent.llm.ollama_client import OllamaClient
from research_agent.observability.logging_config import (
    configure_logging,
    log_function,
)
from research_agent.services.research_service import (
    ResearchRunner,
    ResearchService,
)
from research_agent.agent.graph import ResearchGraph
from research_agent.storage.database import Database
from research_agent.storage.repositories import ReportRepository
from research_agent.tools.registry import create_tool_registry


@log_function
def create_app(
    settings: Settings | None = None,
    research_service: ResearchRunner | None = None,
) -> FastAPI:
    """Construct the FastAPI app, allowing dependencies to be replaced in tests."""
    app_settings = settings or Settings.from_environment()
    configure_logging(getattr(logging, app_settings.log_level))
    database = Database(app_settings.database_path)
    report_repository = ReportRepository(database)

    if research_service is None:
        tools = create_tool_registry(app_settings)
        llm = OllamaClient(
            app_settings.ollama_base_url,
            app_settings.ollama_model,
            timeout=app_settings.request_timeout_seconds * 3,
        )
        graph = ResearchGraph(tools.search, tools.fetch, tools.extract, llm)
        research_service = ResearchService(graph, report_repository)

    app = FastAPI(
        title="Internet Research Agent",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.research_service = research_service
    app.state.report_repository = report_repository
    app.include_router(router)
    register_error_handlers(app)
    return app


app = create_app()


@log_function
def run() -> None:
    """Run the API server using configured host and port."""
    settings = Settings.from_environment()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
