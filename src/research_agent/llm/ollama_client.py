"""Ollama HTTP client implemented with the Python standard library."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from research_agent.observability.logging_config import log_function


class OllamaClient:
    """Call Ollama's local ``/api/generate`` endpoint."""

    @log_function
    def __init__(
        self, base_url: str, model: str, timeout: float = 60
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    @log_function
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
        except HTTPError as exc:
            detail = exc.read(2048).decode("utf-8", errors="replace").strip()
            try:
                error_payload = json.loads(detail)
            except json.JSONDecodeError:
                error_message = detail or exc.reason
            else:
                error_message = error_payload.get("error", detail or exc.reason)
            hint = ""
            if exc.code == 404 and "model" in str(error_message).lower():
                hint = (
                    " Check OLLAMA_MODEL and run `ollama list`; if the model is "
                    "not installed, run `ollama pull <model>`."
                )
            raise RuntimeError(
                f"Ollama generation failed (HTTP {exc.code}): "
                f"{error_message}.{hint}"
            ) from exc
        except (TimeoutError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama generation failed: {exc}") from exc
        generated = result.get("response")
        if not isinstance(generated, str) or not generated.strip():
            raise RuntimeError("Ollama returned an empty or invalid response")
        return generated.strip()
