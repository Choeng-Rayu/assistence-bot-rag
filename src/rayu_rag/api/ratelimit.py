"""In-memory rate limiting, mirrored from ``lib/supportBot/rateLimit.ts``.

Owner: Reach.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["LimitResult", "consume_global", "consume_ip"]


@dataclass(frozen=True, slots=True)
class LimitResult:
    """Result of consuming one request against a limiter."""

    ok: bool
    remaining: int
    reset_at: int
    retry_after_sec: int


def consume_ip(ip: str, now: int | None = None) -> LimitResult:
    """Consume one request for *ip* against the sliding window and daily cap.

    ``RAYU_BOT_IP_WINDOW_LIMIT`` (6) requests per
    ``RAYU_BOT_IP_WINDOW_MINUTES`` (10) minutes plus
    ``RAYU_BOT_IP_DAILY_LIMIT`` (50) per UTC day. Nothing is counted unless both
    budgets allow the request. *now* is injectable milliseconds for tests.

    TODO(Reach): implement the per-IP limiter.
    """

    raise NotImplementedError("TODO(Reach): implement consume_ip")


def consume_global(now: int | None = None) -> LimitResult:
    """Consume one request against the process-wide UTC-day cap.

    Cap is ``RAYU_BOT_GLOBAL_DAILY_LIMIT`` (500).

    TODO(Reach): implement the global limiter.
    """

    raise NotImplementedError("TODO(Reach): implement consume_global")
