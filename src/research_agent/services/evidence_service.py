"""Evidence collection and management service."""

from collections import deque
from urllib.parse import urldefrag, urlsplit, urlunsplit

from research_agent.models.evidence import EvidenceItem, SearchHit
from research_agent.observability.logging_config import log_function
from research_agent.tools.base import PageFetcher, PageExtractor

_STOP_WORDS = {
    "about", "after", "also", "from", "have", "into", "more", "that",
    "their", "there", "these", "this", "what", "when", "where", "which",
    "with", "would", "your", "does", "will", "should", "could",
}
_SKIP_PATH_PARTS = {"/login", "/signin", "/signup", "/privacy", "/terms", "/cookie"}


@log_function
def normalize_url(url: str) -> str:
    """Normalize a source URL for duplicate detection."""
    parts = urlsplit(urldefrag(url).url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


def _query_terms(query: str) -> set[str]:
    return {
        token.lower().strip(".,:;!?()[]{}")
        for token in query.split()
        if len(token.strip(".,:;!?()[]{}")) > 2
        and token.lower() not in _STOP_WORDS
    }


@log_function
def collect_evidence(
    hits: list[SearchHit],
    fetcher: PageFetcher,
    extractor: PageExtractor,
    *,
    max_pages: int,
    max_chars_per_page: int,
    query: str = "",
) -> list[EvidenceItem]:
    """Fetch search results and a bounded set of relevant same-site links."""
    if max_pages < 1 or max_chars_per_page < 1:
        raise ValueError("page and character limits must be positive")

    queue = deque((hit, 0) for hit in hits)
    collected: list[EvidenceItem] = []
    seen_urls: set[str] = set()
    terms = _query_terms(query)

    while queue and len(collected) < max_pages:
        hit, depth = queue.popleft()
        normalized = normalize_url(hit.url)
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)
        try:
            page = fetcher.fetch(hit.url)
            content = extractor.extract(page)[:max_chars_per_page].strip()
            if not content:
                continue
            link_extractor = getattr(extractor, "extract_links", None)
            discovered = link_extractor(page) if callable(link_extractor) else []
            links = list(dict.fromkeys(url for url, _anchor in discovered))
            collected.append(EvidenceItem(
                title=hit.title or page.title or hit.url,
                url=page.url or hit.url,
                snippet=hit.snippet,
                content=content,
                links=links,
            ))

            if depth == 0 and terms and len(collected) < max_pages:
                page_host = (urlsplit(page.url or hit.url).hostname or "").lower()
                relevant: list[SearchHit] = []
                for link, anchor in discovered:
                    parts = urlsplit(link)
                    path = parts.path.lower()
                    if (parts.hostname or "").lower() != page_host:
                        continue
                    if any(part in path for part in _SKIP_PATH_PARTS):
                        continue
                    haystack = f"{anchor} {path.replace('-', ' ').replace('_', ' ')}".lower()
                    if not any(term in haystack for term in terms):
                        continue
                    if normalize_url(link) in seen_urls:
                        continue
                    relevant.append(SearchHit(
                        title=anchor or link,
                        url=link,
                        snippet="Relevant internal link discovered on a search result page",
                    ))
                for follow_hit in reversed(relevant[:max_pages - len(collected)]):
                    queue.appendleft((follow_hit, 1))
        except (OSError, RuntimeError, ValueError):
            continue

    return collected
