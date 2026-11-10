"""Ranker registry: name -> owning module (implemented data).

Owner: Tanchhay.
"""

from __future__ import annotations

#: Public ranker names mapped to the module that owns their implementation.
RANKERS: dict[str, str] = {
    "keyword": "rayu_rag.ranking.keyword",
    "tfidf": "rayu_rag.ranking.tfidf",
    "bm25": "rayu_rag.ranking.bm25",
    "fusion": "rayu_rag.ranking.fusion",
}

__all__ = ["RANKERS"]
