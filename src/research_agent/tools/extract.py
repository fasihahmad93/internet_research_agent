"""Dependency-free HTML text extraction."""

from html.parser import HTMLParser

from research_agent.observability.logging_config import log_function
from research_agent.tools.base import FetchedPage


class _TextParser(HTMLParser):
    _ignored = {"script", "style", "noscript", "svg", "nav", "footer"}

    @log_function
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, _attrs: list[tuple[str, str | None]]
    ) -> None:
        del _attrs
        if tag.lower() in self._ignored:
            self._ignored_depth += 1
        elif not self._ignored_depth and tag.lower() in {"p", "div", "br", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._ignored and self._ignored_depth:
            self._ignored_depth -= 1
        elif not self._ignored_depth and tag.lower() in {"p", "div", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


class HtmlPageExtractor:
    """Extract readable text while omitting common non-content elements."""

    @log_function
    def extract(self, page: FetchedPage) -> str:
        parser = _TextParser()
        parser.feed(page.html)
        return "\n".join(
            line.strip()
            for line in "".join(parser.parts).splitlines()
            if line.strip()
        )
