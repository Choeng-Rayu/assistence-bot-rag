"""GET /api/docs and the debug-only GET /api/retrieve.

Owner: Reach.
"""

from __future__ import annotations

from fastapi import FastAPI

__all__ = ["register"]


def register(app: FastAPI) -> None:
    """Attach the docs and debug-retrieval routes to *app*.

    ``GET /api/docs`` lists document metadata (slug, title, source URL, chunk
    count). ``GET /api/retrieve?q=&k=&ranker=`` runs retrieval for debugging and
    is only mounted when ``RAYU_RAG_DEBUG=1``.

    TODO(Reach): implement the docs and debug-retrieval routes.
    """

    raise NotImplementedError("TODO(Reach): implement routes_docs.register")
