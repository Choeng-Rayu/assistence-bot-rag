"""HTTP API for the RayuCode RAG assistant.

Owner: Reach. Every route and helper is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Reach)`` message until P5 lands.
"""

from __future__ import annotations

from .app import create_app

__all__ = ["create_app"]
