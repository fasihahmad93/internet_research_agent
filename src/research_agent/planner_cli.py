"""Command-line interface for generating research plans."""

import argparse
import logging
import sys

from pydantic import ValidationError

from research_agent.agent.planner import ResearchPlanner
from research_agent.config import Settings
from research_agent.llm.ollama_client import OllamaClient
from research_agent.observability.logging_config import (
    configure_logging,
    log_function,
)


@log_function
def main() -> int:
    """Parse a research question, call the configured model, and print JSON."""
    parser = argparse.ArgumentParser(
        description="Create a structured web-research plan for a query."
    )
    parser.add_argument("query", help="Research question to plan")
    args = parser.parse_args()

    try:
        settings = Settings.from_environment()
        configure_logging(getattr(logging, settings.log_level))
        llm = OllamaClient(
            settings.ollama_base_url,
            settings.ollama_model,
            timeout=settings.request_timeout_seconds * 3,
        )
        plan = ResearchPlanner(llm).plan(args.query)
    except (OSError, RuntimeError, ValueError, ValidationError) as exc:
        print(f"Could not create research plan: {exc}", file=sys.stderr)
        return 1

    print(plan.model_dump_json(indent=2))
    return 0
