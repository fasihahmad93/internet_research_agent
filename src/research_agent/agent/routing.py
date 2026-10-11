"""Conditional routing for the research graph."""

from research_agent.agent.state import ResearchState


def route_after_search(state: ResearchState) -> str:
    """Select evidence collection when search returned usable pages."""
    return "collect_evidence" if state.search_hits else "no_results"
