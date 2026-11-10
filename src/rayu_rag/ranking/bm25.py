"""Okapi BM25 ranker.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, ScoredChunk

__all__ = ["BM25Ranker"]


class BM25Ranker:
    """Okapi BM25 over the inverted index.

    Scoring formula::

        idf(t)      = log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)
        score(d, q) = sum over t in q of
                      idf(t) * tf(t,d) * (k1 + 1)
                      / (tf(t,d) + k1 * (1 - b + b * dl(d) / avgdl))

    Parameters are tuned on the dev split only; the sweep grid is
    ``k1 in {0.9, 1.2, 1.5}`` and ``b in {0, 0.75, 1}``. The default
    ``k1=1.2, b=0.75`` is the untuned baseline.
    """

    name = "bm25"

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Return the top *k* chunks by BM25 score.

        ``components["bm25"]`` holds the score; term-level contributions may be
        added for debugging.

        TODO(Tanchhay): implement BM25 scoring.
        """

        raise NotImplementedError("TODO(Tanchhay): implement BM25Ranker.rank")
