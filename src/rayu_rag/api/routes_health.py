"""GET /api/health — service and index status.

Owner: Reach.
"""

from __future__ import annotations

from fastapi import FastAPI

__all__ = ["register"]


def register(app: FastAPI) -> None:
    """Attach the health route to *app*.

    Returns ``status``, ``index_version`` (the index ``corpus_version``),
    ``chunk_count``, ``ranker`` and ``llm_mode``.

    TODO(Reach): implement the health route.
    """

    raise NotImplementedError("TODO(Reach): implement routes_health.register")
