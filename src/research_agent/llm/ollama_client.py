"""Ollama HTTP client implemented with the Python standard library."""

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


class OllamaClient:
    """Call Ollama's local ``/api/generate`` endpoint."""

    def __init__(
        self, base_url: str, model: str, timeout: float = 60
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        payload = json.dumps(
            {"model": self._model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        request = Request(
            f"{self._base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama generation failed: {exc}") from exc
        generated = result.get("response")
        if not isinstance(generated, str) or not generated.strip():
            raise RuntimeError("Ollama returned an empty or invalid response")
        return generated.strip()
