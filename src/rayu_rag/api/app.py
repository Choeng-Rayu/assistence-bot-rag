"""FastAPI application factory.

Owner: Reach.
"""

from __future__ import annotations

from fastapi import FastAPI

from ..config import Config

__all__ = ["create_app"]


def create_app(config: Config | None = None) -> FastAPI:
    """Build the FastAPI app (routes, static frontend, lifespan).

    Expected wiring once implemented:

    * ``config`` defaults to :meth:`rayu_rag.config.Config.from_env`;
    * register the chat, health, docs and (debug-gated) retrieve routers;
    * serve ``web/`` at ``/`` and ``/static/*``;
    * load the index at startup and expose health metadata.

    TODO(Reach): implement the application factory.
    """

    raise NotImplementedError("TODO(Reach): implement create_app")
