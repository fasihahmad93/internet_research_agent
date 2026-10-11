"""Small in-process counters for basic operational visibility."""

from collections import Counter
from threading import Lock

_counts: Counter[str] = Counter()
_lock = Lock()


def increment(name: str) -> None:
    """Increment a named counter in a thread-safe manner."""
    with _lock:
        _counts[name] += 1


def snapshot() -> dict[str, int]:
    """Return a copy of all counters."""
    with _lock:
        return dict(_counts)
