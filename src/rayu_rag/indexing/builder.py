"""Build the serializable inverted-index artifact.

Owner: Somnang.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..contracts import Chunk, IndexArtifact

__all__ = ["build_index"]


def build_index(chunks: Sequence[Chunk], manifest: dict) -> IndexArtifact:
    """Build an :class:`~rayu_rag.contracts.IndexArtifact` from *chunks*.

    Requirements:

    * ``postings`` keyed by stemmed term, each list sorted by ``chunk_id``;
    * ``doc_lengths`` maps ``chunk_id`` -> token count;
    * ``avgdl`` is the mean document length (``0.0`` for an empty corpus);
    * ``corpus_version`` is the first 12 hex characters of the SHA-256 over the
      canonical documents + chunks payload, so equal corpora give equal bytes;
    * output is byte-stable across builds (no timestamps, no dict-order drift).

    TODO(Somnang): implement deterministic index construction.
    """

    raise NotImplementedError("TODO(Somnang): implement build_index")
