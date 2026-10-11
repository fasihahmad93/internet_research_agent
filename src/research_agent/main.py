"""Application entry point."""

import uvicorn
from fastapi import FastAPI

from research_agent.api.routes import router
from research_agent.config import Settings

app = FastAPI(title="Internet Research Agent", version="0.1.0")
app.include_router(router)


def run() -> None:
    """Run the API server using configured host and port."""
    settings = Settings.from_environment()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
