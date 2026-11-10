"""Corpus preparation: slugging, chunking, document metadata, and manifests.

Owner: Nike. Every algorithm in this package is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Nike)`` message until P1 lands.
"""

from __future__ import annotations

from .chunker import chunk_document, slugify
from .manifest import build_manifest, verify_manifest
from .prepare import prepare_corpus

__all__ = [
    "build_manifest",
    "chunk_document",
    "prepare_corpus",
    "slugify",
    "verify_manifest",
]
