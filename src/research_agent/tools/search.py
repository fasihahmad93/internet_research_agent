"""DuckDuckGo HTML search provider using the Python standard library."""

import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from research_agent.models.evidence import SearchHit
from research_agent.observability.logging_config import log_function


def _destination_url(url: str) -> str:
    """Unwrap DuckDuckGo result redirect URLs."""
    parts = urlsplit(url)
    if "duckduckgo.com" in (parts.hostname or ""):
        target = parse_qs(parts.query).get("uddg", [""])[0]
        if target.startswith(("http://", "https://")):
            return target
    return url


class _DuckDuckGoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hits: list[SearchHit] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag.lower() == "a" and "result__a" in classes:
            self._current = {
                "url": _destination_url(attributes.get("href", "")),
                "title": "",
                "snippet": "",
            }
            self._capture = "title"
        elif tag.lower() in {"a", "div"} and "result__snippet" in classes:
            self._capture = "snippet"

    def handle_data(self, data: str) -> None:
        if self._capture == "title" and self._current is not None:
            self._current["title"] += data
        elif self._capture == "snippet" and self.hits:
            previous = self.hits[-1]
            self.hits[-1] = previous.model_copy(
                update={"snippet": f"{previous.snippet}{data}"}
            )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._capture == "title" and self._current is not None:
            if self._current["url"].startswith(("http://", "https://")):
                self._current["title"] = " ".join(self._current["title"].split())
                self.hits.append(SearchHit(**self._current))
            self._current = None
            self._capture = None
        elif tag.lower() in {"a", "div"} and self._capture == "snippet":
            self._capture = None


class DuckDuckGoSearch:
    """Search DuckDuckGo HTML with bounded retries for transient failures."""

    @log_function
    def __init__(self, timeout: float = 15, retries: int = 2) -> None:
        if timeout <= 0 or retries < 0:
            raise ValueError("timeout must be positive and retries cannot be negative")
        self._timeout = timeout
        self._retries = retries

    @log_function
    def search(self, query: str, limit: int) -> list[SearchHit]:
        query = query.strip()
        if not query:
            raise ValueError("query cannot be empty")
        if limit < 1:
            raise ValueError("limit must be at least 1")
        url = f"https://html.duckduckgo.com/html/?{urlencode({'q': query})}"
        last_error: Exception | None = None
        for attempt in range(self._retries + 1):
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; InternetResearchAgent/0.1)",
                    "Accept": "text/html",
                },
            )
            try:
                with urlopen(request, timeout=self._timeout) as response:
                    html = response.read(2_000_000).decode("utf-8", errors="replace")
                parser = _DuckDuckGoParser()
                parser.feed(html)
                return parser.hits[:limit]
            except HTTPError as exc:
                last_error = exc
                if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                    raise RuntimeError(f"Search request failed: HTTP {exc.code}") from exc
            except (TimeoutError, URLError) as exc:
                last_error = exc
            if attempt < self._retries:
                time.sleep(min(0.25 * (2**attempt), 1.0))
        raise RuntimeError(
            f"Search failed after {self._retries + 1} attempts: {last_error}"
        ) from last_error
