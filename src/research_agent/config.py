"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from research_agent.observability.logging_config import log_function

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROMPT_FILE = Path(__file__).resolve().parent / "agent" / "prompts.yaml"


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the API, database, and local model integration."""

    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5"
    database_path: Path = Path("data/research_agent.sqlite3")
    request_timeout_seconds: float = 20.0
    max_response_bytes: int = 2_000_000
    prompt_file: Path = DEFAULT_PROMPT_FILE
    log_level: str = "INFO"

    @classmethod
    @log_function
    def from_environment(cls) -> "Settings":
        """Build settings from environment variables with validated values."""
        load_dotenv(PROJECT_ROOT / ".env", override=False)
        try:
            port = int(os.getenv("PORT", str(cls.port)))
            timeout = float(
                os.getenv("REQUEST_TIMEOUT_SECONDS", str(cls.request_timeout_seconds))
            )
            max_response_bytes = int(
                os.getenv("MAX_RESPONSE_BYTES", str(cls.max_response_bytes))
            )
        except ValueError as exc:
            raise ValueError(
                "PORT, REQUEST_TIMEOUT_SECONDS, and MAX_RESPONSE_BYTES "
                "must be valid numeric values"
            ) from exc
        if not 1 <= port <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        if timeout <= 0 or not float("-inf") < timeout < float("inf"):
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be positive")
        if max_response_bytes <= 0:
            raise ValueError("MAX_RESPONSE_BYTES must be positive")
        log_level = os.getenv("LOG_LEVEL", cls.log_level).upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(
                "LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL"
            )

        database_path = Path(
            os.getenv("DATABASE_PATH", str(cls.database_path))
        ).expanduser()
        if not database_path.is_absolute():
            database_path = PROJECT_ROOT / database_path
        prompt_file = Path(
            os.getenv("PROMPT_FILE", str(DEFAULT_PROMPT_FILE))
        ).expanduser()
        if not prompt_file.is_absolute():
            prompt_file = PROJECT_ROOT / prompt_file

        return cls(
            app_env=os.getenv("APP_ENV", cls.app_env),
            host=os.getenv("HOST", cls.host),
            port=port,
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL", cls.ollama_base_url
            ).rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", cls.ollama_model),
            database_path=database_path,
            request_timeout_seconds=timeout,
            max_response_bytes=max_response_bytes,
            prompt_file=prompt_file,
            log_level=log_level,
        )
