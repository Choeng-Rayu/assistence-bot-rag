"""Corpus preparation entry point.

Owner: Nike.
"""

from __future__ import annotations

from pathlib import Path

from ..contracts import Chunk, DocumentMeta

__all__ = ["prepare_corpus"]


def prepare_corpus(
    docs_dir: Path,
    out_dir: Path,
) -> tuple[list[DocumentMeta], list[Chunk]]:
    """Chunk every ``*.md`` file in *docs_dir* and write corpus artifacts.

    Writes ``documents.jsonl`` and ``chunks.jsonl`` under *out_dir* and returns
    the in-memory ``(documents, chunks)`` pair. Ordering must be deterministic:
    documents by slug, chunks by document order then ``part_index``.

    Only the 14 frozen documents are expected; ``README`` files are skipped.

    TODO(Nike): implement deterministic corpus preparation and artifact writing.
    """

    raise NotImplementedError("TODO(Nike): implement prepare_corpus")
