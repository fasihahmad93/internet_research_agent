"""Research graph node implementations."""

from research_agent.agent.state import ResearchState
from research_agent.agent.prompts import report_prompt
from research_agent.llm.base import LanguageModel
from research_agent.llm.structured_output import generate_structured
from research_agent.models.report import ReportDraft, ResearchReport
from research_agent.services.citation_service import validate_citations
from research_agent.services.depth_policy import limits_for
from research_agent.services.evidence_service import collect_evidence
from research_agent.services.quality_service import score_report
from research_agent.tools.base import PageExtractor, PageFetcher, SearchProvider


def search_node(state: ResearchState, search: SearchProvider) -> None:
    limits = limits_for(state.request.depth)
    state.search_hits = search.search(state.request.query, limits.max_results)


def evidence_node(
    state: ResearchState,
    fetcher: PageFetcher,
    extractor: PageExtractor,
) -> None:
    limits = limits_for(state.request.depth)
    state.evidence = collect_evidence(
        state.search_hits,
        fetcher,
        extractor,
        max_pages=limits.max_pages,
        max_chars_per_page=limits.max_chars_per_page,
    )


def report_node(state: ResearchState, llm: LanguageModel) -> None:
    if not state.evidence:
        raise ValueError("Search returned no fetchable evidence")
    draft = generate_structured(
        llm, report_prompt(state.request.query, state.evidence), ReportDraft
    )
    validate_citations(draft, state.evidence)
    state.report = ResearchReport(
        query=state.request.query,
        title=draft.title,
        summary=draft.summary,
        findings=draft.findings,
        citations=state.evidence,
        quality_score=score_report(draft, state.evidence),
    )
