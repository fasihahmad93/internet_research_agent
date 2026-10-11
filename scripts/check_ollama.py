"""Check whether the local Ollama service is reachable."""

import logging
from urllib.error import URLError
from urllib.request import urlopen

from research_agent.config import Settings
from research_agent.observability.logging_config import (
    configure_logging,
    log_function,
)


@log_function
def main() -> int:
    settings = Settings.from_environment()
    configure_logging(getattr(logging, settings.log_level))
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        with urlopen(url, timeout=5) as response:
            print(f"Ollama is reachable (HTTP {response.status}).")
            return 0
    except (TimeoutError, URLError) as exc:
        print(f"Could not reach Ollama at {url}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
