"""Persist and load the index artifact.

Owner: Somnang.
"""

from __future__ import annotations

from pathlib import Path

from ..contracts import IndexArtifact, LoadedIndex

__all__ = ["load_index", "write_index"]


def write_index(artifact: IndexArtifact, out_dir: Path) -> None:
    """Write *artifact* to *out_dir* as canonical ``index.json`` + ``chunks.jsonl``.

    The output must be byte-stable: canonical JSON (sorted keys, compact
    separators, UTF-8, trailing newline) and deterministically ordered rows.

    TODO(Somnang): implement atomic, canonical index writes.
    """

    raise NotImplementedError("TODO(Somnang): implement write_index")


def load_index(index_dir: Path) -> LoadedIndex:
    """Load ``index.json`` + ``chunks.jsonl`` from *index_dir*.

    Returns chunks materialized as :class:`~rayu_rag.contracts.LoadedIndex` with
    a ``by_id`` mapping for O(1) chunk lookup.

    TODO(Somnang): implement index loading.
    """

    raise NotImplementedError("TODO(Somnang): implement load_index")
