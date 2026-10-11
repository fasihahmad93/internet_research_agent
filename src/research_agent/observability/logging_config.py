"""Application logging configuration."""

import inspect
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a consistent console logging format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger(__name__).debug(
        "logging.configured level=%s", logging.getLevelName(level)
    )


def log_function(function: Callable[P, R]) -> Callable[P, R]:
    """Log function lifecycle at DEBUG without logging argument or result values."""
    logger = logging.getLogger(function.__module__)
    name = function.__qualname__

    if inspect.iscoroutinefunction(function):
        async_function = cast(Callable[P, Awaitable[R]], function)

        @wraps(function)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started_at = perf_counter()
            logger.debug("function.started name=%s", name)
            try:
                result = await async_function(*args, **kwargs)
            except Exception as exc:
                logger.warning(
                    "function.failed name=%s error_type=%s",
                    name,
                    type(exc).__name__,
                )
                raise
            logger.debug(
                "function.completed name=%s duration_ms=%.2f",
                name,
                (perf_counter() - started_at) * 1000,
            )
            return result

        return cast(Callable[P, R], async_wrapper)

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = perf_counter()
        logger.debug("function.started name=%s", name)
        try:
            result = function(*args, **kwargs)
        except Exception as exc:
            logger.warning(
                "function.failed name=%s error_type=%s",
                name,
                type(exc).__name__,
            )
            raise
        logger.debug(
            "function.completed name=%s duration_ms=%.2f",
            name,
            (perf_counter() - started_at) * 1000,
        )
        return result

    return wrapper
