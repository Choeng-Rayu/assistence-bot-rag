"""TF-IDF + cosine ranker (evaluation baseline).

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, ScoredChunk

__all__ = ["TfidfRanker"]


class TfidfRanker:
    """Classic TF-IDF baseline with cosine similarity.

    ``idf = log(N / df)``; vectors use ``tf * idf`` for each term and cosine
    similarity over the query and chunk vectors. Used mainly to compare against
    BM25 in the evaluation harness.

    TODO(Tanchhay): implement the TF-IDF/cosine ranker.
    """

    name = "tfidf"

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Return the top *k* chunks by TF-IDF cosine similarity.

        TODO(Tanchhay): implement TfidfRanker.rank.
        """

        raise NotImplementedError("TODO(Tanchhay): implement TfidfRanker.rank")
