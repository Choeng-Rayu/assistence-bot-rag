"""TF-IDF + cosine ranker (evaluation baseline).

Owner: Tanchhay.
"""

from __future__ import annotations

import math
from collections import Counter

from ..contracts import IndexArtifact, LoadedIndex, ScoredChunk
from ..indexing.tokenizer import tokenize
from ._util import finalize

__all__ = ["TfidfRanker"]

_NORM_CACHE: dict[tuple[str, int], dict[str, float]] = {}


def _doc_norms(artifact: IndexArtifact) -> dict[str, float]:
    """Euclidean norm of every chunk's tf*idf vector (cached per corpus)."""

    key = (artifact.corpus_version, artifact.chunk_count)
    cached = _NORM_CACHE.get(key)
    if cached is not None:
        return cached
    n = artifact.chunk_count
    squares: dict[str, float] = {}
    for plist in artifact.postings.values():
        idf = math.log(n / len(plist))
        for posting in plist:
            squares[posting.chunk_id] = squares.get(posting.chunk_id, 0.0) + (posting.tf * idf) ** 2
    norms = {chunk_id: math.sqrt(total) for chunk_id, total in squares.items()}
    _NORM_CACHE[key] = norms
    return norms


class TfidfRanker:
    """Classic TF-IDF baseline with cosine similarity.

    ``idf = log(N / df)``; vectors use ``tf * idf`` for each term and cosine
    similarity over the query and chunk vectors. Used mainly to compare against
    BM25 in the evaluation harness.
    """

    name = "tfidf"

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Return the top *k* chunks by TF-IDF cosine similarity."""

        artifact = index.artifact
        n = artifact.chunk_count
        if n == 0:
            return []
        query_tf = Counter(tokenize(query, for_query=True))
        norms = _doc_norms(artifact)

        dots: dict[str, float] = {}
        query_sq = 0.0
        for term, qtf in query_tf.items():
            plist = artifact.postings.get(term)
            if not plist:
                continue
            idf = math.log(n / len(plist))
            q_weight = qtf * idf
            query_sq += q_weight**2
            for posting in plist:
                dots[posting.chunk_id] = dots.get(posting.chunk_id, 0.0) + q_weight * posting.tf * idf
        query_norm = math.sqrt(query_sq)
        if query_norm == 0.0:
            return []

        rows = []
        for chunk_id, dot in dots.items():
            chunk = index.by_id.get(chunk_id)
            denom = norms.get(chunk_id, 0.0) * query_norm
            if chunk is None or denom == 0.0:
                continue
            score = dot / denom
            rows.append((chunk, score, {"tfidf": score}))
        return finalize(rows, k)
