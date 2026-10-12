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
    """Fetch unique search hits and capture links discovered on each page."""
    if max_pages < 1 or max_chars_per_page < 1:
        raise ValueError("page and character limits must be positive")
    collected: list[EvidenceItem] = []
    seen_urls: set[str] = set()
    for hit in hits:
        if normalize_url(hit.url) in seen_urls:
            continue
        seen_urls.add(normalize_url(hit.url))
        try:
            page = fetcher.fetch(hit.url)
            content = extractor.extract(page)[:max_chars_per_page].strip()
            if not content:
                continue
            link_extractor = getattr(extractor, "extract_links", None)
            discovered = link_extractor(page) if callable(link_extractor) else []
            links = list(dict.fromkeys(url for url, anchor in discovered))
            collected.append(EvidenceItem(
                title=hit.title or page.title or hit.url,
                url=page.url or hit.url,
                snippet=hit.snippet,
                content=content,
                links=links,
            ))
        except (OSError, RuntimeError, ValueError):
            continue
        if len(collected) >= max_pages:
            break
    return collected
