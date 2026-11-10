"""Rankers and the shared retrieval pipeline.

Owner: Tanchhay. Every algorithm in this package is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Tanchhay)`` message until P3/P4 land.
"""

from __future__ import annotations

from ..contracts import Ranker
from .base import build_ranker
from .bm25 import BM25Ranker
from .fusion import FusionRanker
from .keyword import KeywordRanker
from .retrieve import retrieve
from .tfidf import TfidfRanker

__all__ = [
    "BM25Ranker",
    "FusionRanker",
    "KeywordRanker",
    "Ranker",
    "TfidfRanker",
    "build_ranker",
    "retrieve",
]
