"""Tests for environment-driven configuration and YAML prompts."""

import pytest

from research_agent.agent.prompts import report_prompt
from research_agent.config import Settings


def test_settings_read_values_from_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8123")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://model.test/")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reports.sqlite3"))
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("MAX_RESPONSE_BYTES", "4096")
    prompt_file = tmp_path / "prompts.yaml"
    prompt_file.write_text("report: 'Research {query} using {sources}'\n")
    monkeypatch.setenv("PROMPT_FILE", str(prompt_file))

    settings = Settings.from_environment()

    assert settings.app_env == "test"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8123
    assert settings.ollama_base_url == "http://model.test"
    assert settings.ollama_model == "test-model"
    assert settings.database_path == tmp_path / "reports.sqlite3"
    assert settings.request_timeout_seconds == 4.5
    assert settings.max_response_bytes == 4096
    assert settings.prompt_file == prompt_file


def test_report_prompt_uses_configured_yaml(monkeypatch, tmp_path) -> None:
    prompt_file = tmp_path / "prompts.yaml"
    prompt_file.write_text(
        "report: |\n  Query: {query}\n  Evidence:\n  {sources}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROMPT_FILE", str(prompt_file))

    result = report_prompt("Research question", [])

    assert "Query: Research question" in result
    assert "Evidence:" in result


def test_report_prompt_errors_on_missing_template(monkeypatch, tmp_path) -> None:
    prompt_file = tmp_path / "prompts.yaml"
    prompt_file.write_text("other: ignored\n", encoding="utf-8")
    monkeypatch.setenv("PROMPT_FILE", str(prompt_file))

    with pytest.raises(ValueError, match="non-empty 'report' string"):
        report_prompt("Research question", [])


def test_settings_reject_non_numeric_port(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "invalid")

    with pytest.raises(ValueError, match="valid numeric values"):
        Settings.from_environment()


def test_settings_reject_invalid_log_level(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "TRACE")

    with pytest.raises(ValueError, match="LOG_LEVEL must be"):
        Settings.from_environment()
