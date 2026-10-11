"""Research lifecycle event definitions."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchEvent:
    """Structured event emitted during a research run."""

    name: str
    attributes: dict[str, Any]
    occurred_at: datetime


def emit_event(name: str, **attributes: Any) -> ResearchEvent:
    """Create and log an event without exposing sensitive request contents."""
    event = ResearchEvent(name, attributes, datetime.now(UTC))
    logger.info("research_event name=%s attributes=%s", name, attributes)
    return event
