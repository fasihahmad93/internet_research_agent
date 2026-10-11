"""Research request and result domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from research_agent.observability.logging_config import log_function


class ResearchDepth(StrEnum):
    """How broad a search should be."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class ResearchRequest(BaseModel):
    """Validated request to research a question."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=5, max_length=500)
    depth: ResearchDepth = ResearchDepth.STANDARD

    @field_validator("query")
    @classmethod
    @log_function
    def query_must_contain_non_whitespace(cls, query: str) -> str:
        if not query.strip():
            raise ValueError("query must contain non-whitespace characters")
        return query
