"""Structured research-plan model."""

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """A planner's decomposition of a research question."""

    objective: str = Field(min_length=1)
    subquestions: list[str] = Field(min_length=1, max_length=8)
    steps: list[str] = Field(min_length=1, max_length=8)
    search_queries: list[str] = Field(min_length=1, max_length=8)
