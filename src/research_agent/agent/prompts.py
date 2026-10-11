"""Prompt templates for research tasks."""

import yaml

from research_agent.config import Settings
from research_agent.models.evidence import EvidenceItem


def report_prompt(query: str, evidence: list[EvidenceItem]) -> str:
    """Load and render the source-grounded report prompt from YAML."""
    prompt_file = Settings.from_environment().prompt_file
    try:
        with prompt_file.open(encoding="utf-8") as stream:
            prompt_data = yaml.safe_load(stream)
    except OSError as exc:
        raise RuntimeError(f"Could not read prompt YAML file: {prompt_file}") from exc

    template = prompt_data.get("report") if isinstance(prompt_data, dict) else None
    if not isinstance(template, str) or not template.strip():
        raise ValueError(
            f"Prompt YAML file must define a non-empty 'report' string: {prompt_file}"
        )

    sources = "\n\n".join(
        f"Evidence ID: {item.id}\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Content: {item.content}"
        for item in evidence
    )
    try:
        return template.format(query=query, sources=sources)
    except (KeyError, ValueError) as exc:
        raise ValueError(
            f"Prompt YAML report template has invalid placeholders: {prompt_file}"
        ) from exc
