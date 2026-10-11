"""API route tests."""

from fastapi.testclient import TestClient

from research_agent.config import Settings
from research_agent.main import create_app
from research_agent.models.report import ResearchReport
from research_agent.models.research import ResearchRequest


class StubResearchService:
    def research(self, request: ResearchRequest) -> ResearchReport:
        return ResearchReport(
            query=request.query,
            title="Test report",
            summary="Test summary",
            findings=[],
            citations=[],
            quality_score=0,
        )


def test_health_check_returns_ok(tmp_path) -> None:
    app = create_app(
        Settings(database_path=tmp_path / "test.sqlite3"),
        StubResearchService(),
    )
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_endpoint_returns_report(tmp_path) -> None:
    app = create_app(
        Settings(database_path=tmp_path / "test.sqlite3"),
        StubResearchService(),
    )
    response = TestClient(app).post(
        "/research", json={"query": "What is a test?", "depth": "quick"}
    )

    assert response.status_code == 200
    assert response.json()["report"]["title"] == "Test report"
