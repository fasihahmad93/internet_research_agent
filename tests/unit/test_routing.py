"""Unit tests for research graph routing."""

from research_agent.agent.routing import route_after_search
from research_agent.agent.state import ResearchState
from research_agent.models.evidence import SearchHit
from research_agent.models.research import ResearchRequest


def test_routes_empty_search_to_no_results() -> None:
    state = ResearchState(request=ResearchRequest(query="sample question"))

    assert route_after_search(state) == "no_results"


def test_routes_search_hits_to_evidence_collection() -> None:
    state = ResearchState(
        request=ResearchRequest(query="sample question"),
        search_hits=[
            SearchHit(title="Result", url="https://example.test")
        ],
    )

    assert route_after_search(state) == "collect_evidence"
