"""Fusion ranker: BM25 primary plus a keyword tie-breaker.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, Ranker, ScoredChunk
from ._util import finalize
from .keyword import KeywordRanker, query_identifiers

__all__ = ["FusionRanker"]

#: Fixed boost for a chunk containing an identifier from the query verbatim.
IDENTIFIER_BOOST = 0.15


def _min_max(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    low, high = min(scores.values()), max(scores.values())
    if high == low:
        return {key: 1.0 for key in scores}
    return {key: (value - low) / (high - low) for key, value in scores.items()}


class FusionRanker:
    """Blend a primary ranker with the keyword baseline.

    The fused score is ``alpha * primary_score + (1 - alpha) * keyword_score``
    after each ranker is min-max normalized; an exact-identifier match adds a
    fixed boost. ``alpha=0.5`` was chosen on the dev split (``scripts/tune_rankers.py``), never on the hold-out.

    Production candidate once BM25 and keyword both exist.
    """

    name = "fusion"

    def __init__(self, primary: Ranker, alpha: float = 0.5) -> None:
        self.primary = primary
        self.alpha = alpha
        self._keyword = KeywordRanker()

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Return the top *k* chunks by the fused score.

        ``components`` records ``primary``, ``keyword`` and ``identifier``
        contributions.
        """

        depth = max(len(index.chunks), k)
        primary_hits = self.primary.rank(query, index, k=depth)
        keyword_hits = self._keyword.rank(query, index, k=depth)
        primary = _min_max({h.chunk.chunk_id: h.score for h in primary_hits})
        keyword = _min_max({h.chunk.chunk_id: h.score for h in keyword_hits})
        by_id = {h.chunk.chunk_id: h.chunk for h in (*keyword_hits, *primary_hits)}
        identifiers = query_identifiers(query)

        rows = []
        for chunk_id, chunk in by_id.items():
            p = self.alpha * primary.get(chunk_id, 0.0)
            kw = (1.0 - self.alpha) * keyword.get(chunk_id, 0.0)
            text = chunk.text.lower()
            ident = IDENTIFIER_BOOST if any(i in text for i in identifiers) else 0.0
            rows.append((chunk, p + kw + ident, {"primary": p, "keyword": kw, "identifier": ident}))
        return finalize(rows, k)
