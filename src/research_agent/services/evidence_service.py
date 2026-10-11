"""Evidence collection and management service."""

from urllib.parse import urldefrag, urlsplit, urlunsplit

from research_agent.models.evidence import EvidenceItem, SearchHit
from research_agent.observability.logging_config import log_function
from research_agent.tools.base import PageFetcher, PageExtractor


@log_function
def normalize_url(url: str) -> str:
    """Normalize a source URL for duplicate detection."""
    parts = urlsplit(urldefrag(url).url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


@log_function
def collect_evidence(
    hits: list[SearchHit],
    fetcher: PageFetcher,
    extractor: PageExtractor,
    *,
    max_pages: int,
    max_chars_per_page: int,
) -> list[EvidenceItem]:
    """Fetch unique search hits and convert them into evidence items."""
    collected: list[EvidenceItem] = []
    seen_urls: set[str] = set()
    for hit in hits:
        normalized = normalize_url(hit.url)
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)
        page = fetcher.fetch(hit.url)
        content = extractor.extract(page)[:max_chars_per_page].strip()
        if not content:
            continue
        collected.append(
            EvidenceItem(
                title=hit.title or page.title or hit.url,
                url=hit.url,
                snippet=hit.snippet,
                content=content,
            )
        )
        if len(collected) >= max_pages:
            break
    return collected
