"""Unit tests for the research-depth policy."""

from research_agent.models.research import ResearchDepth
from research_agent.services.depth_policy import limits_for


def test_deeper_research_has_more_sources_and_pages() -> None:
    quick = limits_for(ResearchDepth.QUICK)
    standard = limits_for(ResearchDepth.STANDARD)
    deep = limits_for(ResearchDepth.DEEP)

    assert quick.max_results < standard.max_results < deep.max_results
    assert quick.max_pages < standard.max_pages < deep.max_pages


def test_depth_limits_bound_page_content() -> None:
    assert limits_for(ResearchDepth.QUICK).max_chars_per_page == 8_000
