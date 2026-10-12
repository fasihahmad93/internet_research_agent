"""Web-page fetching tool with bounded retries and response limits."""

import ssl
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import certifi

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
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)


class HttpPageFetcher:
    """Fetch bounded HTTP(S) pages and retry transient network/server failures."""

    @log_function
    def __init__(
        self, timeout: float = 15, max_bytes: int = 2_000_000, retries: int = 2
    ) -> None:
        if timeout <= 0 or max_bytes < 1 or retries < 0:
            raise ValueError("timeout and max_bytes must be positive; retries cannot be negative")
        self._timeout = timeout
        self._max_bytes = max_bytes
        self._retries = retries

    @log_function
    def fetch(self, url: str) -> FetchedPage:
        parsed = urlsplit(url)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError("Only absolute HTTP(S) URLs without credentials can be fetched")

        last_error: Exception | None = None
        for attempt in range(self._retries + 1):
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; InternetResearchAgent/0.1)",
                    "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8,*/*;q=0.1",
                },
            )
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                with urlopen(request, timeout=self._timeout, context=ssl_context) as response:
                    content_type = response.headers.get_content_type()
                    if content_type not in {"text/html", "application/xhtml+xml", "text/plain"}:
                        raise ValueError(f"Unsupported page content type: {content_type}")
                    raw = response.read(self._max_bytes + 1)
                    if len(raw) > self._max_bytes:
                        raise ValueError(
                            f"Page exceeded configured limit of {self._max_bytes} bytes"
                        )
                    html = raw.decode("utf-8", errors="replace")
                    final_url = response.geturl()
                final = urlsplit(final_url)
                if final.scheme.lower() not in {"http", "https"} or not final.hostname:
                    raise ValueError("Redirected to an unsupported URL")
                title_parser = _TitleParser()
                title_parser.feed(html)
                title = " ".join(" ".join(title_parser.parts).split())
                return FetchedPage(final_url, html, title)
            except HTTPError as exc:
                last_error = exc
                if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                    raise OSError(f"Could not fetch {url}: HTTP {exc.code}") from exc
            except (TimeoutError, URLError) as exc:
                last_error = exc
            if attempt < self._retries:
                time.sleep(min(0.25 * (2**attempt), 1.0))

        raise OSError(
            f"Could not fetch {url} after {self._retries + 1} attempts: {last_error}"
        ) from last_error
