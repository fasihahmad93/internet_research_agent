"""Generate a research plan from a query using the configured Ollama model."""

import logging
import sys
from pathlib import Path

# Allow running this script directly from a source checkout without an editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from research_agent.config import Settings
from research_agent.observability.logging_config import configure_logging
from research_agent.planner_cli import main


if __name__ == "__main__":
    settings = Settings.from_environment()
    configure_logging(getattr(logging, settings.log_level))
    logging.getLogger(__name__).info("Starting research planner")
    raise SystemExit(main())
