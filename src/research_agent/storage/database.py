"""SQLite database initialization and connection management."""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from research_agent.observability.logging_config import log_function


class Database:
    """Small SQLite wrapper used by repositories."""

    @log_function
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        logger = logging.getLogger(__name__)
        logger.debug("database.connection.started")
        try:
            if str(self.path) != ":memory:":
                self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.path)
            connection.row_factory = sqlite3.Row
        except Exception as exc:
            logger.warning(
                "database.connection.failed error_type=%s", type(exc).__name__
            )
            raise
        try:
            yield connection
            connection.commit()
            logger.debug("database.connection.committed")
        except Exception as exc:
            connection.rollback()
            logger.warning(
                "database.connection.rolled_back error_type=%s",
                type(exc).__name__,
            )
            raise
        finally:
            connection.close()

    @log_function
    def initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_reports (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_checkpoints (
                    id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
