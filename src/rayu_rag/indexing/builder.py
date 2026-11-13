"""Build the serializable inverted-index artifact.

Owner: Somnang.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

from ..contracts import Chunk, IndexArtifact, SCHEMA_VERSION
from .postings import build_postings

__all__ = ["build_index"]

# Increment this string whenever the tokenizer algorithm changes so that
# cached indexes built with an old tokenizer are detected as stale.
TOKENIZER_VERSION = "1"


def _corpus_version(chunks: Sequence[Chunk], manifest: dict) -> str:
    """Compute a 12-hex-character corpus version fingerprint.

    The fingerprint is the first 12 characters of the SHA-256 of a canonical
    JSON payload that covers the manifest (which embeds per-file sha256 hashes)
    plus chunk ids and their text. Equal corpora produce equal bytes.
    """
    # Build a minimal, deterministic payload.
    # Sorting is crucial for byte-stability across Python dict orderings.
    payload = {
        "manifest": manifest,
        "chunks": [
            {"chunk_id": c.chunk_id, "text": c.text}
            for c in sorted(chunks, key=lambda c: c.chunk_id)
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return digest[:12]


def build_index(chunks: Sequence[Chunk], manifest: dict) -> IndexArtifact:
    """Build an :class:`~rayu_rag.contracts.IndexArtifact` from *chunks*.

    Steps:
    1. Build postings + doc_lengths via :func:`~rayu_rag.indexing.postings.build_postings`.
    2. Compute ``avgdl`` as the mean token count across all chunks
       (``0.0`` for an empty corpus — avoids ZeroDivisionError).
    3. Compute a 12-hex-char ``corpus_version`` from the canonical chunk
       + manifest payload so equal corpora give equal bytes.
    4. Return a fully populated :class:`~rayu_rag.contracts.IndexArtifact`.

    The result is byte-stable: postings keys are sorted, posting lists are
    sorted by ``chunk_id``, and ``chunk_ids`` is a sorted tuple.
    """
    postings, doc_lengths = build_postings(chunks)

    # Average document length (number of tokens)
    if doc_lengths:
        avgdl = sum(doc_lengths.values()) / len(doc_lengths)
    else:
        avgdl = 0.0

    corpus_ver = _corpus_version(chunks, manifest)

    # chunk_ids must be a sorted tuple for deterministic Boolean complement
    chunk_ids = tuple(sorted(c.chunk_id for c in chunks))

    return IndexArtifact(
        schema_version=SCHEMA_VERSION,
        corpus_version=corpus_ver,
        tokenizer_version=TOKENIZER_VERSION,
        chunk_count=len(chunks),
        avgdl=avgdl,
        chunk_ids=chunk_ids,
        postings=postings,
        doc_lengths=doc_lengths,
    )
