"""Web-page fetching tool."""

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from research_agent.observability.logging_config import log_function
from research_agent.tools.base import FetchedPage


class _TitleParser(HTMLParser):
    @log_function
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, _attrs: list[tuple[str, str | None]]
    ) -> None:
        del _attrs
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)


class HttpPageFetcher:
    """Fetch bounded HTTP(S) pages with a descriptive user agent."""

    @log_function
    def __init__(self, timeout: float = 15, max_bytes: int = 2_000_000) -> None:
        self._timeout = timeout
        self._max_bytes = max_bytes

    @log_function
    def fetch(self, url: str) -> FetchedPage:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Only absolute HTTP(S) URLs can be fetched")
        request = Request(url, headers={"User-Agent": "InternetResearchAgent/0.1"})
        try:
            with urlopen(request, timeout=self._timeout) as response:
                content_type = response.headers.get_content_type()
                if not content_type.startswith("text/"):
                    raise ValueError(f"Unsupported page content type: {content_type}")
                html = response.read(self._max_bytes).decode("utf-8", errors="replace")
                final_url = response.geturl()
        except (TimeoutError, URLError) as exc:
            raise OSError(f"Could not fetch {url}: {exc}") from exc
        title_parser = _TitleParser()
        title_parser.feed(html)
        return FetchedPage(final_url, html, " ".join(" ".join(title_parser.parts).split()))
