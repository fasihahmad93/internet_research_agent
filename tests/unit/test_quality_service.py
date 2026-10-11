"""Unit tests for research quality evaluation."""

from uuid import uuid4

from research_agent.models.evidence import EvidenceItem
from research_agent.models.report import ReportDraft, ReportFinding
from research_agent.services.quality_service import score_report


def test_score_rewards_supported_findings_and_source_diversity() -> None:
    first = EvidenceItem(id=uuid4(), title="A", url="https://a.test", content="a")
    second = EvidenceItem(id=uuid4(), title="B", url="https://b.test", content="b")
    draft = ReportDraft(
        title="Report",
        summary="Summary",
        findings=[ReportFinding(text="Claim", evidence_ids=[first.id])],
    )

    assert score_report(draft, [first, second]) == 0.9


def test_no_evidence_scores_zero() -> None:
    draft = ReportDraft(title="Report", summary="Summary")

    assert score_report(draft, []) == 0
