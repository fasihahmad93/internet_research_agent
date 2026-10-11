"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the API and local model integration."""

    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from environment variables."""
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            ),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        )
