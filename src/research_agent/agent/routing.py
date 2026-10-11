"""Conditional routing for the research graph."""

from research_agent.agent.state import ResearchState
from research_agent.observability.logging_config import log_function


@log_function
def route_after_search(state: ResearchState) -> str:
    """Select evidence collection when search returned usable pages."""
    return "collect_evidence" if state.search_hits else "no_results"
