"""Shared helpers for the rankers.

Owner: Tanchhay.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from ..contracts import Chunk, ScoredChunk

__all__ = ["finalize"]


def finalize(
    scored: Iterable[tuple[Chunk, float, Mapping[str, float]]],
    k: int,
) -> list[ScoredChunk]:
    """Sort by score desc then document order, keep *k*, assign 1-based ranks."""

    ordered = sorted(scored, key=lambda row: (-row[1], row[0].order, row[0].chunk_id))
    return [
        ScoredChunk(chunk=chunk, score=score, rank=position, components=dict(components))
        for position, (chunk, score, components) in enumerate(ordered[: max(k, 0)], start=1)
    ]
