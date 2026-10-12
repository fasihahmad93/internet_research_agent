"""Tests for robust web extraction and bounded same-site link discovery."""

from research_agent.models.evidence import SearchHit
from research_agent.services.evidence_service import collect_evidence
from research_agent.tools.base import FetchedPage
from research_agent.tools.extract import HtmlPageExtractor


def test_extractor_returns_readable_text_and_absolute_links() -> None:
    page = FetchedPage(
        url="https://example.com/research/start",
        html=(
            "<html><head><script>ignore me</script></head><body>"
            "<h1>Research overview</h1><p>Useful evidence here.</p>"
            '<a href="/research/python-agents#section">Python agents</a>'
            '<a href="mailto:hello@example.com">Email</a>'
            '<a href="https://other.example/page">External page</a>'
            "</body></html>"
        ),
    )
    extractor = HtmlPageExtractor()

    text = extractor.extract(page)
    links = extractor.extract_links(page)

    assert "Research overview" in text
    assert "Useful evidence here." in text
    assert "ignore me" not in text
    assert ("https://example.com/research/python-agents", "Python agents") in links
    assert all(not url.startswith("mailto:") for url, _ in links)


def test_evidence_collection_follows_relevant_same_site_link_within_limit() -> None:
    class StubFetcher:
        def __init__(self) -> None:
            self.visited: list[str] = []

        def fetch(self, url: str) -> FetchedPage:
            self.visited.append(url)
            if url.endswith("/start"):
                html = (
                    "<h1>Research start</h1><p>Initial evidence.</p>"
                    '<a href="/python-agents">Python agents details</a>'
                    '<a href="https://other.example/python-agents">External result</a>'
                )
            else:
                html = "<h1>Python agents</h1><p>Additional evidence.</p>"
            return FetchedPage(url=url, html=html, title="Test page")

    fetcher = StubFetcher()
    evidence = collect_evidence(
        [SearchHit(title="Start", url="https://example.com/start")],
        fetcher,
        HtmlPageExtractor(),
        max_pages=2,
        max_chars_per_page=1000,
        query="python agents",
    )

    assert len(evidence) == 2
    assert fetcher.visited == [
        "https://example.com/start",
        "https://example.com/python-agents",
    ]
    assert evidence[0].links == ["https://example.com/python-agents", "https://other.example/python-agents"]


def test_evidence_collection_rejects_invalid_limits() -> None:
    class UnusedFetcher:
        def fetch(self, url: str) -> FetchedPage:
            raise AssertionError("fetch should not be called")

    import pytest

    with pytest.raises(ValueError, match="limits must be positive"):
        collect_evidence(
            [],
            UnusedFetcher(),
            HtmlPageExtractor(),
            max_pages=0,
            max_chars_per_page=100,
        )
