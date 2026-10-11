"""Tests for the research planner."""

import json

import pytest

from research_agent.agent.planner import ResearchPlanner, build_planner_prompt
from research_agent.models.plan import ResearchPlan


class StubLlm:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompt = ""

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return self.response


def test_planner_creates_a_valid_plan_from_model_output() -> None:
    response = json.dumps(
        {
            "objective": "Understand heat pumps",
            "subquestions": ["How do they transfer heat?"],
            "steps": ["Find trusted explainers"],
            "search_queries": ["how heat pumps work"],
        }
    )
    llm = StubLlm(response)

    plan = ResearchPlanner(llm).plan("How do heat pumps work?")

    assert plan.objective == "Understand heat pumps"
    assert plan.search_queries == ["how heat pumps work"]
    assert "How do heat pumps work?" in llm.prompt
    assert "JSON Schema" in llm.prompt


def test_planner_rejects_too_short_query() -> None:
    with pytest.raises(ValueError, match="between 5 and 500"):
        ResearchPlanner(StubLlm("{}")).plan("Why?")


def test_build_planner_prompt_reads_yaml_file(tmp_path) -> None:
    prompt_file = tmp_path / "prompts.yaml"
    prompt_file.write_text("planner: 'Plan this: {query}'\n", encoding="utf-8")

    prompt = build_planner_prompt("A sample question", prompt_file)

    assert prompt == "Plan this: A sample question"


def test_planner_model_has_bounded_query_lists() -> None:
    with pytest.raises(ValueError):
        ResearchPlan(
            objective="Objective",
            subquestions=[],
            steps=["Step"],
            search_queries=["query"],
        )
