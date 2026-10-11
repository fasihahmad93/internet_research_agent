"""Research quality evaluation service."""

from research_agent.models.evidence import EvidenceItem
from research_agent.observability.logging_config import log_function
from research_agent.models.report import ReportDraft


@log_function
def score_report(draft: ReportDraft, evidence: list[EvidenceItem]) -> float:
    """Score source coverage, source diversity, and supported findings."""
    if not evidence:
        return 0.0

    evidence_ids = {item.id for item in evidence}
    covered_findings = sum(
        bool(set(finding.evidence_ids) & evidence_ids)
        for finding in draft.findings
    )
    coverage = covered_findings / max(len(draft.findings), 1)
    diversity = min(len({item.url for item in evidence}) / 3, 1)
    return round(0.7 * coverage + 0.3 * diversity, 3)
