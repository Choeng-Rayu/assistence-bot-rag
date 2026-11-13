"""Inverted-index postings and sorted set operations.

Owner: Somnang.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from ..contracts import Chunk, Posting, Postings
from .tokenizer import tokenize

__all__ = ["build_postings", "complement", "intersect", "union"]


def build_postings(chunks: Sequence[Chunk]) -> tuple[Postings, dict[str, int]]:
    """Build ``(postings, doc_lengths)`` from *chunks*.

    For every chunk:
    - tokenize its text
    - count term frequency (tf) per chunk
    - record ``Posting(chunk_id, tf)``

    ``postings[term]`` is a list of :class:`~rayu_rag.contracts.Posting`
    sorted by ``chunk_id`` (alphabetical).

    ``doc_lengths[chunk_id]`` is the total token count for that chunk,
    which BM25 uses to normalise against average document length.
    """
    # term -> {chunk_id -> count}
    tf_map: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    doc_lengths: dict[str, int] = {}

    for chunk in chunks:
        tokens = tokenize(chunk.text)
        doc_lengths[chunk.chunk_id] = len(tokens)
        for token in tokens:
            tf_map[token][chunk.chunk_id] += 1

    # Build sorted posting lists
    postings: Postings = {}
    for term, chunk_counts in tf_map.items():
        postings[term] = [
            Posting(chunk_id=cid, tf=count)
            for cid, count in sorted(chunk_counts.items())
        ]

    return postings, doc_lengths


def intersect(a: Sequence[str], b: Sequence[str]) -> list[str]:
    """Sorted intersection of two sorted id lists — Boolean AND.

    Uses a linear two-pointer merge so the time complexity is O(n + m).
    Both inputs must already be sorted; output is sorted.

    Example::

        intersect(["a", "b", "c"], ["b", "c", "d"]) == ["b", "c"]
    """
    result: list[str] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return result


def union(a: Sequence[str], b: Sequence[str]) -> list[str]:
    """Sorted union of two sorted id lists — Boolean OR.

    Uses a linear two-pointer merge so the time complexity is O(n + m).
    Both inputs must already be sorted; output is sorted and deduplicated.

    Example::

        union(["a", "b"], ["b", "c"]) == ["a", "b", "c"]
    """
    result: list[str] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    # Drain whichever list has remaining items
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def complement(ids: Sequence[str], universe: Sequence[str]) -> list[str]:
    """Sorted ``universe - ids`` — Boolean NOT.

    Returns every id in *universe* that does NOT appear in *ids*.
    Both inputs must already be sorted; output is sorted.

    Example::

        complement(["b"], ["a", "b", "c"]) == ["a", "c"]
    """
    result: list[str] = []
    ids_set = set(ids)  # O(1) lookup; ids is typically small
    for uid in universe:
        if uid not in ids_set:
            result.append(uid)
    return result
