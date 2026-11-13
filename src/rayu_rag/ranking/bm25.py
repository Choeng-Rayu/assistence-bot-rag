"""Okapi BM25 ranker.

Owner: Tanchhay.
"""

from __future__ import annotations

import math

from ..contracts import LoadedIndex, ScoredChunk
from ..indexing.tokenizer import tokenize
from ._util import finalize

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

        ``components["bm25"]`` holds the score; term-level contributions are
        recorded as ``term:<term>``.
        """

        artifact = index.artifact
        n = artifact.chunk_count
        if n == 0:
            return []
        avgdl = artifact.avgdl or 1.0

        scores: dict[str, float] = {}
        parts: dict[str, dict[str, float]] = {}
        for term in tokenize(query, for_query=True):
            plist = artifact.postings.get(term)
            if not plist:
                continue
            df = len(plist)
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
            for posting in plist:
                dl = artifact.doc_lengths.get(posting.chunk_id, 0)
                norm = self.k1 * (1.0 - self.b + self.b * dl / avgdl)
                contribution = idf * posting.tf * (self.k1 + 1.0) / (posting.tf + norm)
                scores[posting.chunk_id] = scores.get(posting.chunk_id, 0.0) + contribution
                parts.setdefault(posting.chunk_id, {})[f"term:{term}"] = contribution

        rows = []
        for chunk_id, score in scores.items():
            chunk = index.by_id.get(chunk_id)
            if chunk is None:
                continue
            rows.append((chunk, score, {"bm25": score, **parts[chunk_id]}))
        return finalize(rows, k)
