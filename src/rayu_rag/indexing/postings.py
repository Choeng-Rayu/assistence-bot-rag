"""Inverted-index postings and sorted set operations.

Owner: Somnang.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..contracts import Chunk, Postings

__all__ = ["build_postings", "complement", "intersect", "union"]


def build_postings(chunks: Sequence[Chunk]) -> tuple[Postings, dict[str, int]]:
    """Build ``(postings, doc_lengths)`` from *chunks*.

    ``postings[term]`` is a list of :class:`~rayu_rag.contracts.Posting` sorted
    by ``chunk_id``; ``doc_lengths[chunk_id]`` is the token count used by BM25.

    TODO(Somnang): implement postings construction with sorted, deduplicated ids.
    """

    raise NotImplementedError("TODO(Somnang): implement build_postings")


def intersect(a: Sequence[str], b: Sequence[str]) -> list[str]:
    """Sorted intersection of two sorted id lists (linear merge).

    TODO(Somnang): implement sorted intersection.
    """

    raise NotImplementedError("TODO(Somnang): implement intersect")


def union(a: Sequence[str], b: Sequence[str]) -> list[str]:
    """Sorted union of two sorted id lists (linear merge).

    TODO(Somnang): implement sorted union.
    """

    raise NotImplementedError("TODO(Somnang): implement union")


def complement(ids: Sequence[str], universe: Sequence[str]) -> list[str]:
    """Sorted ``universe - ids`` for sorted inputs (Boolean NOT).

    TODO(Somnang): implement sorted complement.
    """

    raise NotImplementedError("TODO(Somnang): implement complement")
