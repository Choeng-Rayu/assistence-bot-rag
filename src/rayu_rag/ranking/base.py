"""Ranker factory and shared registry.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import Ranker

__all__ = ["build_ranker"]


def build_ranker(name: str) -> Ranker:
    """Return the ranker registered under *name*.

    Known names: ``keyword`` (:class:`~rayu_rag.ranking.keyword.KeywordRanker`),
    ``tfidf`` (:class:`~rayu_rag.ranking.tfidf.TfidfRanker`), ``bm25``
    (:class:`~rayu_rag.ranking.bm25.BM25Ranker`) and ``fusion``
    (:class:`~rayu_rag.ranking.fusion.FusionRanker`, BM25 primary).

    An unknown name raises :class:`ValueError`.
    """

    from .bm25 import BM25Ranker
    from .fusion import FusionRanker
    from .keyword import KeywordRanker
    from .tfidf import TfidfRanker

    key = name.strip().lower()
    if key == "keyword":
        return KeywordRanker()
    if key == "tfidf":
        return TfidfRanker()
    if key == "bm25":
        return BM25Ranker()
    if key == "fusion":
        return FusionRanker(BM25Ranker())
    raise ValueError(f"unknown ranker {name!r}; expected keyword, tfidf, bm25 or fusion")
