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


def test_api_documentation_is_available(tmp_path) -> None:
    app = create_app(
        Settings(database_path=tmp_path / "test.sqlite3"),
        StubResearchService(),
    )
    client = TestClient(app)

    docs_response = client.get("/docs")
    redoc_response = client.get("/redoc")
    schema_response = client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert "Swagger UI" in docs_response.text
    assert redoc_response.status_code == 200
    assert "ReDoc" in redoc_response.text
    assert schema_response.status_code == 200
    assert "/research" in schema_response.json()["paths"]
