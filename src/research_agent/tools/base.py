"""Shared interfaces and transport models for research tools."""

from dataclasses import dataclass
from typing import Protocol

from research_agent.models.evidence import SearchHit


class SearchProvider(Protocol):
    """Search provider interface."""

    def search(self, query: str, limit: int) -> list[SearchHit]: ...


@dataclass(frozen=True)
class FetchedPage:
    """Raw HTML response from a web page."""

    url: str
    html: str
    title: str = ""


class PageFetcher(Protocol):
    """Web-page retrieval interface."""

    def fetch(self, url: str) -> FetchedPage: ...


class PageExtractor(Protocol):
    """Convert a fetched page into readable text."""

    def extract(self, page: FetchedPage) -> str: ...
