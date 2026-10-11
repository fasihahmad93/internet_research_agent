"""Research graph checkpoint persistence."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from research_agent.observability.logging_config import log_function
from research_agent.storage.database import Database


class CheckpointRepository:
    """Persist opaque JSON state snapshots for later workflow resumption."""

    @log_function
    def __init__(self, database: Database) -> None:
        self._database = database

    @log_function
    def save(self, state: dict[str, object]) -> str:
        checkpoint_id = str(uuid4())
        self._database.initialize()
        with self._database.connection() as connection:
            connection.execute(
                """
                INSERT INTO graph_checkpoints (id, state_json, created_at)
                VALUES (?, ?, ?)
                """,
                (checkpoint_id, json.dumps(state), datetime.now(UTC).isoformat()),
            )
        return checkpoint_id

    @log_function
    def get(self, checkpoint_id: str) -> dict[str, object] | None:
        self._database.initialize()
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT state_json FROM graph_checkpoints WHERE id = ?",
                (checkpoint_id,),
            ).fetchone()
        return json.loads(row["state_json"]) if row else None
