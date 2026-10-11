"""Unit tests for report and checkpoint persistence."""

from research_agent.models.report import ResearchReport
from research_agent.storage.checkpoints import CheckpointRepository
from research_agent.storage.database import Database
from research_agent.storage.repositories import ReportRepository


def test_report_repository_round_trips_report(tmp_path) -> None:
    repository = ReportRepository(Database(tmp_path / "research.sqlite3"))
    report = ResearchReport(
        query="What is a sample?",
        title="Sample report",
        summary="A short summary.",
        findings=[],
        citations=[],
        quality_score=0,
    )

    repository.save(report)

    assert repository.get(str(report.id)) == report


def test_checkpoint_repository_round_trips_state(tmp_path) -> None:
    repository = CheckpointRepository(Database(tmp_path / "research.sqlite3"))
    state = {"stage": "search", "attempt": 1}

    checkpoint_id = repository.save(state)

    assert repository.get(checkpoint_id) == state
