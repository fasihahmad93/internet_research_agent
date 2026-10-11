"""Small deterministic research graph runner."""

from research_agent.agent.nodes import evidence_node, report_node, search_node
from research_agent.agent.routing import route_after_search
from research_agent.agent.state import ResearchState
from research_agent.llm.base import LanguageModel
from research_agent.models.research import ResearchRequest
from research_agent.models.report import ResearchReport
from research_agent.observability.logging_config import log_function
from research_agent.tools.base import PageExtractor, PageFetcher, SearchProvider


class ResearchGraph:
    """Execute search, evidence collection, and report generation in order."""

    @log_function
    def __init__(
        self,
        search: SearchProvider,
        fetcher: PageFetcher,
        extractor: PageExtractor,
        llm: LanguageModel,
    ) -> None:
        self._search = search
        self._fetcher = fetcher
        self._extractor = extractor
        self._llm = llm

    @log_function
    def run(self, request: ResearchRequest) -> ResearchReport:
        state = ResearchState(request=request)
        search_node(state, self._search)
        if route_after_search(state) == "no_results":
            raise ValueError("Search did not return any results")
        evidence_node(state, self._fetcher, self._extractor)
        report_node(state, self._llm)
        if state.report is None:
            raise RuntimeError("Research graph completed without a report")
        return state.report
