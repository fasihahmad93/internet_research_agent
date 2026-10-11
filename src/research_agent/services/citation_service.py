"""Citation formatting and validation service."""

from research_agent.models.evidence import EvidenceItem
from research_agent.models.report import ReportDraft


def format_citation(evidence: EvidenceItem, number: int) -> str:
    """Format a source as a compact numbered citation."""
    return f"[{number}] {evidence.title}. {evidence.url}"


def validate_citations(
    draft: ReportDraft, evidence: list[EvidenceItem]
) -> None:
    """Raise when a finding cites evidence that was not gathered."""
    available_ids = {item.id for item in evidence}
    unknown = {
        evidence_id
        for finding in draft.findings
        for evidence_id in finding.evidence_ids
        if evidence_id not in available_ids
    }
    if unknown:
        raise ValueError(f"Report contains unknown evidence IDs: {sorted(unknown)}")
