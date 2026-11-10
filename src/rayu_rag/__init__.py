"""RayuCode docs-only RAG support assistant.

The package is deliberately light on import: heavy dependencies (FastAPI,
uvicorn, httpx) are only imported by the modules that need them. The CLI uses
lazy imports inside its handlers so ``python -m rayu_rag --help`` always works.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
