"""Language-model client interface."""

from typing import Protocol


class LanguageModel(Protocol):
    """Minimal text-generation interface used by the research workflow."""

    def generate(self, prompt: str) -> str: ...
