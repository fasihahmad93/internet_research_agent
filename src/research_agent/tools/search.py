"""DuckDuckGo HTML search provider using only the Python standard library."""

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from research_agent.models.evidence import SearchHit
from research_agent.observability.logging_config import log_function


class _DuckDuckGoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hits: list[SearchHit] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag == "a" and "result__a" in classes:
            self._current = {
                "url": attributes.get("href", ""),
                "title": "",
                "snippet": "",
            }
            self._capture = "title"
        elif tag in {"a", "div"} and "result__snippet" in classes and self.hits:
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
        if tag == "a" and self._capture == "title" and self._current is not None:
            if self._current["url"]:
                self.hits.append(SearchHit(**self._current))
            self._current = None
            self._capture = None
        elif tag in {"a", "div"} and self._capture == "snippet":
            self._capture = None


class DuckDuckGoSearch:
    """Search the public DuckDuckGo HTML endpoint."""

    @log_function
    def __init__(self, timeout: float = 15) -> None:
        self._timeout = timeout

    @log_function
    def search(self, query: str, limit: int) -> list[SearchHit]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        url = f"https://html.duckduckgo.com/html/?{urlencode({'q': query})}"
        request = Request(url, headers={"User-Agent": "InternetResearchAgent/0.1"})
        try:
            with urlopen(request, timeout=self._timeout) as response:
                html = response.read(2_000_000).decode("utf-8", errors="replace")
        except (TimeoutError, URLError) as exc:
            raise RuntimeError(f"Search request failed: {exc}") from exc
        parser = _DuckDuckGoParser()
        parser.feed(html)
        return parser.hits[:limit]
