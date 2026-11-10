"""POST /api/support-chat — streaming chat, mirrored from ``route.ts``.

Owner: Reach.
"""

from __future__ import annotations

from fastapi import FastAPI

__all__ = ["register"]


def register(app: FastAPI) -> None:
    """Attach the support-chat route to *app*.

    Contract to mirror from ``app/api/support-chat/route.ts``:

    * request JSON ``{"messages": [{"role", "content"}]}``; 1–12 turns, each
      ≤2,000 chars, ≤8,000 chars total, last turn must be ``user``;
    * response ``application/x-ndjson`` with events in order
      ``sources`` -> ``delta`` (many) -> ``done``;
    * pre-stream errors use ``{"error": code, "message": ...}`` with codes
      ``invalid_request``, ``forbidden_origin``, ``rate_limited``,
      ``not_configured``, ``upstream_auth``, ``capacity``, ``busy``,
      ``upstream``.

    TODO(Reach): implement the chat route.
    """

    raise NotImplementedError("TODO(Reach): implement routes_chat.register")
