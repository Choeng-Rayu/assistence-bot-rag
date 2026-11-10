"""Corpus manifest: provenance and integrity hashes.

Owner: Nike.
"""

from __future__ import annotations

from pathlib import Path

from ..contracts import Chunk, DocumentMeta

__all__ = ["build_manifest", "verify_manifest"]


def build_manifest(
    docs_dir: Path,
    docs: list[DocumentMeta],
    chunks: list[Chunk],
    *,
    source_commit: str,
) -> dict:
    """Build the canonical corpus manifest.

    The manifest records ``source_repo``, ``source_commit``, the number of
    documents/chunks, and per-file ``sha256`` hashes so the corpus can be
    verified and the index ``corpus_version`` can be derived reproducibly.

    TODO(Nike): implement the manifest payload (canonical, timestamp-free).
    """

    raise NotImplementedError("TODO(Nike): implement build_manifest")


def verify_manifest(docs_dir: Path, manifest_path: Path) -> list[str]:
    """Return a list of human-readable problems; ``[]`` means the corpus is valid.

    Checks that every manifest file exists under *docs_dir*, that its SHA-256
    still matches, and that the document/chunk counts agree.

    TODO(Nike): implement manifest verification.
    """

    raise NotImplementedError("TODO(Nike): implement verify_manifest")
