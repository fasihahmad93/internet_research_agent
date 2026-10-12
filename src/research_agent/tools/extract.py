"""Dependency-free HTML text and link extraction."""

from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlsplit

from research_agent.observability.logging_config import log_function
from research_agent.tools.base import FetchedPage


class _TextParser(HTMLParser):
    _ignored = {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"}

    @log_function
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, _attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.lower() in self._ignored:
            self._ignored_depth += 1
        elif not self._ignored_depth and tag.lower() in {
            "p", "div", "br", "li", "h1", "h2", "h3", "h4", "section"
        }:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._ignored and self._ignored_depth:
            self._ignored_depth -= 1
        elif not self._ignored_depth and tag.lower() in {
            "p", "div", "li", "h1", "h2", "h3", "h4", "section"
        }:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


class _LinkParser(HTMLParser):
    """Collect user-visible anchor destinations and their text."""

    @log_function
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.lower() == "a":
            attributes = dict(attrs)
            self._href = attributes.get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(" ".join(self._text).split())))
            self._href = None
            self._text = []


class HtmlPageExtractor:
    """Extract readable text and normalized HTTP(S) links from a fetched page."""

    @log_function
    def extract(self, page: FetchedPage) -> str:
        parser = _TextParser()
        parser.feed(page.html)
        return "\n".join(
            line.strip()
            for line in "".join(parser.parts).splitlines()
            if line.strip()
        )

    @log_function
    def extract_links(self, page: FetchedPage) -> list[tuple[str, str]]:
        """Return unique absolute HTTP(S) links paired with their anchor text."""
        parser = _LinkParser()
        parser.feed(page.html)
        links: list[tuple[str, str]] = []
        seen: set[str] = set()
        for href, text in parser.links:
            absolute = urldefrag(urljoin(page.url, href.strip()))[0]
            parts = urlsplit(absolute)
            if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
                continue
            normalized = parts._replace(
                scheme=parts.scheme.lower(), netloc=parts.netloc.lower()
            ).geturl()
            if normalized not in seen:
                seen.add(normalized)
                links.append((normalized, text))
        return links
