"""Tests for the Ollama HTTP client response contract."""

import json
from unittest.mock import MagicMock, patch

from research_agent.llm.ollama_client import OllamaClient


def test_client_posts_prompt_and_returns_generated_text() -> None:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(
        {"response": "Generated answer"}
    ).encode()

    with patch("research_agent.llm.ollama_client.urlopen", return_value=response) as open_url:
        result = OllamaClient("http://localhost:11434/", "test-model").generate(
            "Prompt"
        )

    assert result == "Generated answer"
    request = open_url.call_args.args[0]
    assert request.full_url == "http://localhost:11434/api/generate"
    assert json.loads(request.data)["model"] == "test-model"
