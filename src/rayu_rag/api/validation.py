"""Request validation, mirrored from ``lib/supportBot/validate.ts``.

Owner: Reach.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["MAX_MESSAGE_CHARS", "MAX_MESSAGES", "MAX_TOTAL_CHARS", "ChatRequest", "validate_messages"]

MAX_MESSAGES = 12
MAX_MESSAGE_CHARS = 2000
MAX_TOTAL_CHARS = 8000


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """The support-chat request body: ``{"messages": [...]}``."""

    messages: Sequence[dict[str, str]]


def validate_messages(messages: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    """Validate and normalize a conversation.

    Rules (from ``validate.ts``): 1–12 turns; each ``role`` is ``user`` or
    ``assistant``; each ``content`` is 1–2,000 chars; the total is ≤8,000 chars;
    the last turn must be from the ``user``. Returns the cleaned message list or
    raises a validation error carrying code ``invalid_request``.

    TODO(Reach): implement message validation.
    """

    raise NotImplementedError("TODO(Reach): implement validate_messages")
