"""Integration tests for the search pipeline."""

from research_agent.models.evidence import SearchHit
from research_agent.services.evidence_service import collect_evidence
from research_agent.tools.base import FetchedPage
from research_agent.tools.extract import HtmlPageExtractor


class StubFetcher:
    def fetch(self, url: str) -> FetchedPage:
        return FetchedPage(
            url,
            "<html><script>ignore()</script><h1>Headline</h1>"
            "<p>Useful page content</p></html>",
            "Page title",
        )


def test_search_hits_become_deduplicated_readable_evidence() -> None:
    hits = [
        SearchHit(title="First", url="https://example.test/page#part"),
        SearchHit(title="Duplicate", url="https://example.test/page#other"),
    ]

    evidence = collect_evidence(
        hits,
        StubFetcher(),
        HtmlPageExtractor(),
        max_pages=3,
        max_chars_per_page=1000,
    )

    assert len(evidence) == 1
    assert evidence[0].title == "First"
    assert "Useful page content" in evidence[0].content
    assert "ignore()" not in evidence[0].content
