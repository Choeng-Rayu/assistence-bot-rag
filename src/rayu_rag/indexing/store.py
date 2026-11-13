"""Persist and load the index artifact.

Owner: Somnang.
"""

from __future__ import annotations

from pathlib import Path

from ..contracts import IndexArtifact, LoadedIndex, Posting, Postings
from ..io import chunk_from_dict, chunk_to_dict, read_json, read_jsonl, write_json, write_jsonl

__all__ = ["load_index", "write_index"]


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _artifact_to_dict(artifact: IndexArtifact) -> dict:
    """Convert an :class:`IndexArtifact` to a plain JSON-serializable dict."""
    return {
        "schema_version": artifact.schema_version,
        "corpus_version": artifact.corpus_version,
        "tokenizer_version": artifact.tokenizer_version,
        "chunk_count": artifact.chunk_count,
        "avgdl": artifact.avgdl,
        "chunk_ids": list(artifact.chunk_ids),  # tuple → list for JSON
        "postings": {
            term: [{"chunk_id": p.chunk_id, "tf": p.tf} for p in posting_list]
            for term, posting_list in sorted(artifact.postings.items())  # sorted keys
        },
        "doc_lengths": dict(sorted(artifact.doc_lengths.items())),  # sorted keys
    }


def _artifact_from_dict(data: dict) -> IndexArtifact:
    """Reconstruct an :class:`IndexArtifact` from the loaded JSON dict."""
    postings: Postings = {
        term: [Posting(chunk_id=p["chunk_id"], tf=int(p["tf"])) for p in plist]
        for term, plist in data["postings"].items()
    }
    return IndexArtifact(
        schema_version=int(data["schema_version"]),
        corpus_version=str(data["corpus_version"]),
        tokenizer_version=str(data["tokenizer_version"]),
        chunk_count=int(data["chunk_count"]),
        avgdl=float(data["avgdl"]),
        chunk_ids=tuple(data["chunk_ids"]),
        postings=postings,
        doc_lengths={k: int(v) for k, v in data["doc_lengths"].items()},
    )


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def write_index(artifact: IndexArtifact, out_dir: Path) -> None:
    """Write *artifact* to *out_dir* as canonical ``index.json``.

    Output guarantees:
    - Sorted JSON keys (via :func:`~rayu_rag.io.write_json`).
    - Posting lists are sorted by ``chunk_id`` (preserved from build).
    - Postings dict keys are sorted alphabetically.
    - ``chunk_ids`` list is sorted.
    - No timestamps or host-specific values.
    - Single trailing newline, UTF-8.

    The function also writes ``chunks.jsonl`` alongside the index so that
    :func:`load_index` can reconstruct the full :class:`LoadedIndex` without
    requiring a separate corpus artifact directory.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write index.json
    write_json(out_dir / "index.json", _artifact_to_dict(artifact))


def load_index(index_dir: Path) -> LoadedIndex:
    """Load ``index.json`` and ``chunks.jsonl`` from *index_dir*.

    Returns a :class:`LoadedIndex` with:
    - ``artifact`` — the reconstructed :class:`IndexArtifact`.
    - ``chunks``   — a tuple of :class:`~rayu_rag.contracts.Chunk` objects.
    - ``by_id``    — a ``{chunk_id: Chunk}`` dict for O(1) lookup.

    ``chunks.jsonl`` is expected in the same directory as ``index.json``.
    If it is absent, ``chunks`` and ``by_id`` will be empty (the index can
    still answer Boolean and BM25 queries via postings alone).
    """
    index_dir = Path(index_dir)
    index_path = index_dir / "index.json"
    chunks_path = index_dir / "chunks.jsonl"

    data = read_json(index_path)
    artifact = _artifact_from_dict(data)

    # Load chunks if available
    if chunks_path.exists():
        raw_chunks = read_jsonl(chunks_path)
        chunks = tuple(chunk_from_dict(row) for row in raw_chunks)
    else:
        chunks = ()

    by_id = {chunk.chunk_id: chunk for chunk in chunks}

    return LoadedIndex(
        artifact=artifact,
        chunks=chunks,
        by_id=by_id,
    )
