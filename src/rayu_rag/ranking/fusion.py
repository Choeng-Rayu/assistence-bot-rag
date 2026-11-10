"""Fusion ranker: BM25 primary plus a keyword tie-breaker.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, Ranker, ScoredChunk

__all__ = ["FusionRanker"]


class FusionRanker:
    """Blend a primary ranker with the keyword baseline.

    The fused score is ``alpha * primary_score + (1 - alpha) * keyword_score``
    after each ranker is min-max normalized; an exact-identifier match adds a
    fixed boost. ``alpha`` is chosen on the dev split, never on the hold-out.

    Production candidate once BM25 and keyword both exist.
    """

    name = "fusion"

    def __init__(self, primary: Ranker, alpha: float = 0.8) -> None:
        self.primary = primary
        self.alpha = alpha

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Return the top *k* chunks by the fused score.

        ``components`` records ``primary``, ``keyword`` and ``identifier``
        contributions.

        TODO(Tanchhay): implement fusion ranking over the configured primary.
        """

        raise NotImplementedError("TODO(Tanchhay): implement FusionRanker.rank")
