"""Registry for the default research tools."""

from dataclasses import dataclass

from research_agent.config import Settings
from research_agent.tools.extract import HtmlPageExtractor
from research_agent.tools.fetch import HttpPageFetcher
from research_agent.tools.search import DuckDuckGoSearch


@dataclass(frozen=True)
class ToolRegistry:
    """Concrete tool collection used by the default application."""

    search: DuckDuckGoSearch
    fetch: HttpPageFetcher
    extract: HtmlPageExtractor


def create_tool_registry(settings: Settings) -> ToolRegistry:
    """Create tools configured with the application's transport limits."""
    return ToolRegistry(
        search=DuckDuckGoSearch(settings.request_timeout_seconds),
        fetch=HttpPageFetcher(
            settings.request_timeout_seconds, settings.max_response_bytes
        ),
        extract=HtmlPageExtractor(),
    )
