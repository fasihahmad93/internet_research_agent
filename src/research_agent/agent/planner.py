"""LLM-backed research query planner."""

import logging
from pathlib import Path

import yaml

from research_agent.config import Settings
from research_agent.llm.base import LanguageModel
from research_agent.llm.structured_output import generate_structured
from research_agent.models.plan import ResearchPlan
from research_agent.observability.logging_config import log_function

logger = logging.getLogger(__name__)


@log_function
def build_planner_prompt(query: str, prompt_file: Path | None = None) -> str:
    """Load and render the planner prompt from the configured YAML file."""
    settings = Settings.from_environment()
    path = prompt_file or settings.prompt_file
    try:
        with path.open(encoding="utf-8") as stream:
            prompt_data = yaml.safe_load(stream)
    except OSError as exc:
        raise RuntimeError(f"Could not read prompt YAML file: {path}") from exc

    template = prompt_data.get("planner") if isinstance(prompt_data, dict) else None
    if not isinstance(template, str) or not template.strip():
        raise ValueError(
            f"Prompt YAML file must define a non-empty 'planner' string: {path}"
        )
    try:
        return template.format(query=query)
    except (KeyError, ValueError) as exc:
        raise ValueError(
            f"Planner prompt template has invalid placeholders: {path}"
        ) from exc


class ResearchPlanner:
    """Create a structured web-research plan from a user query."""

    @log_function
    def __init__(self, llm: LanguageModel) -> None:
        self._llm = llm

    @log_function
    def plan(self, query: str) -> ResearchPlan:
        """Return an actionable and schema-validated research plan."""
        normalized_query = query.strip()
        if not 5 <= len(normalized_query) <= 500:
            raise ValueError("query must contain between 5 and 500 characters")
        logger.info("planner.generation.started query_length=%s", len(normalized_query))
        prompt = build_planner_prompt(normalized_query)
        plan = generate_structured(self._llm, prompt, ResearchPlan)
        logger.info(
            "planner.generation.completed subquestion_count=%s "
            "step_count=%s search_query_count=%s",
            len(plan.subquestions),
            len(plan.steps),
            len(plan.search_queries),
        )
        return plan
