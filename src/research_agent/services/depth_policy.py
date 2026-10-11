"""Research-depth selection policy."""

from dataclasses import dataclass

from research_agent.models.research import ResearchDepth


@dataclass(frozen=True)
class DepthLimits:
    """Resource limits chosen for one research run."""

    max_results: int
    max_pages: int
    max_chars_per_page: int


_LIMITS = {
    ResearchDepth.QUICK: DepthLimits(3, 2, 8_000),
    ResearchDepth.STANDARD: DepthLimits(6, 4, 12_000),
    ResearchDepth.DEEP: DepthLimits(10, 8, 16_000),
}


def limits_for(depth: ResearchDepth) -> DepthLimits:
    """Return search and page limits for the requested depth."""
    return _LIMITS[depth]
