"""Integration tests for the research graph."""

import json

from research_agent.agent.graph import ResearchGraph
from research_agent.models.evidence import SearchHit
from research_agent.models.research import ResearchRequest
from research_agent.tools.base import FetchedPage


class StubSearch:
    def search(self, _query: str, _limit: int) -> list[SearchHit]:
        del _query, _limit
        return [SearchHit(title="Source", url="https://example.test")]


class StubFetcher:
    def fetch(self, url: str) -> FetchedPage:
        return FetchedPage(url, "<p>Evidence supports this claim.</p>", "Source")


class StubExtractor:
    def extract(self, _page: FetchedPage) -> str:
        del _page
        return "Evidence supports this claim."


class StubLlm:
    def generate(self, prompt: str) -> str:
        marker = "Evidence ID: "
        evidence_id = prompt.split(marker, 1)[1].splitlines()[0]
        return json.dumps(
            {
                "title": "Example report",
                "summary": "Evidence supports one claim.",
                "findings": [
                    {"text": "The evidence supports this.", "evidence_ids": [evidence_id]}
                ],
            }
        )


def test_graph_returns_a_report_with_resolved_citations() -> None:
    graph = ResearchGraph(StubSearch(), StubFetcher(), StubExtractor(), StubLlm())

    report = graph.run(ResearchRequest(query="What does this source say?"))

    assert report.title == "Example report"
    assert len(report.citations) == 1
    assert report.findings[0].evidence_ids == [report.citations[0].id]
    assert report.quality_score > 0
