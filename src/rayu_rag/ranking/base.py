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
    (:class:`~rayu_rag.ranking.fusion.FusionRanker`).

    An unknown name must raise :class:`NotImplementedError` (the scaffold has no
    working rankers yet, so this raises for every name for now).

    TODO(Tanchhay): implement the ranker registry and construction.
    """

    raise NotImplementedError("TODO(Tanchhay): implement build_ranker")
