"""Persistence repository implementations."""

from research_agent.models.report import ResearchReport
from research_agent.observability.logging_config import log_function
from research_agent.storage.database import Database


class ReportRepository:
    """Store and retrieve completed research reports."""

    @log_function
    def __init__(self, database: Database) -> None:
        self._database = database

    @log_function
    def save(self, report: ResearchReport) -> None:
        self._database.initialize()
        with self._database.connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO research_reports
                    (id, query, report_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(report.id),
                    report.query,
                    report.model_dump_json(),
                    report.created_at.isoformat(),
                ),
            )

    @log_function
    def get(self, report_id: str) -> ResearchReport | None:
        self._database.initialize()
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT report_json FROM research_reports WHERE id = ?",
                (report_id,),
            ).fetchone()
        return ResearchReport.model_validate_json(row["report_json"]) if row else None
