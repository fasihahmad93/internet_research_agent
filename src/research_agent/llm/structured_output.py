"""Helpers for validating structured language-model output."""

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from research_agent.llm.base import LanguageModel
from research_agent.observability.logging_config import log_function

ModelT = TypeVar("ModelT", bound=BaseModel)


@log_function
def generate_structured(
    llm: LanguageModel, prompt: str, schema: type[ModelT]
) -> ModelT:
    """Ask the model for JSON and validate the response against a Pydantic model."""
    schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
    response = llm.generate(
        f"{prompt}\n\nReturn only valid JSON matching this JSON Schema:\n{schema_json}"
    )
    candidate = response.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.I)
    try:
        return schema.model_validate_json(candidate)
    except (ValidationError, ValueError) as exc:
        raise ValueError(f"Model response did not match {schema.__name__}") from exc
