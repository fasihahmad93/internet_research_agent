"""Small in-process counters for basic operational visibility."""

from collections import Counter
from threading import Lock

from research_agent.observability.logging_config import log_function

_counts: Counter[str] = Counter()
_lock = Lock()


@log_function
def increment(name: str) -> None:
    """Increment a named counter in a thread-safe manner."""
    with _lock:
        _counts[name] += 1


@log_function
def snapshot() -> dict[str, int]:
    """Return a copy of all counters."""
    with _lock:
        return dict(_counts)
