"""Tests for function lifecycle logging."""

import asyncio
import logging

from research_agent.observability.logging_config import log_function


def test_log_function_records_lifecycle_without_arguments(caplog) -> None:
    @log_function
    def example(secret: str) -> str:
        return secret

    with caplog.at_level(logging.DEBUG):
        assert example("sensitive-value") == "sensitive-value"

    assert "function.started name=test_log_function" in caplog.text
    assert "function.completed name=test_log_function" in caplog.text
    assert "sensitive-value" not in caplog.text
    assert "duration_ms=" in caplog.text


def test_log_function_records_failure_type_without_exception_details(caplog) -> None:
    @log_function
    def example(secret: str) -> None:
        raise ValueError(secret)

    with caplog.at_level(logging.DEBUG):
        try:
            example("sensitive-value")
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    assert "function.failed name=test_log_function" in caplog.text
    assert "error_type=ValueError" in caplog.text
    assert "sensitive-value" not in caplog.text


def test_log_function_supports_async_functions(caplog) -> None:
    @log_function
    async def example() -> str:
        return "done"

    with caplog.at_level(logging.DEBUG):
        assert asyncio.run(example()) == "done"

    assert "function.started name=test_log_function" in caplog.text
    assert "function.completed name=test_log_function" in caplog.text
