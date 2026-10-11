"""Unit tests for citation handling."""

from uuid import uuid4

import pytest

from research_agent.models.evidence import EvidenceItem
from research_agent.models.report import ReportDraft, ReportFinding
from research_agent.services.citation_service import (
    format_citation,
    validate_citations,
)


def test_format_citation_includes_number_title_and_url() -> None:
    evidence = EvidenceItem(
        title="Source", url="https://example.test", content="Details"
    )

    assert format_citation(evidence, 2) == "[2] Source. https://example.test"


def test_validate_citations_rejects_unknown_ids() -> None:
    draft = ReportDraft(
        title="Report",
        summary="Summary",
        findings=[ReportFinding(text="Claim", evidence_ids=[uuid4()])],
    )

    with pytest.raises(ValueError, match="unknown evidence IDs"):
        validate_citations(draft, [])
