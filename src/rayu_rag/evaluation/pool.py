"""Pooled judgement candidates.

Owner: Tanchhay.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["build_pool"]


def build_pool(
    *,
    queries_path: Path | None = None,
    qrels_path: Path | None = None,
    index_dir: Path | None = None,
    depth: int = 10,
    random_per_query: int = 5,
    out_path: Path | None = None,
    **kwargs: object,
) -> list[dict]:
    """Build pooled judgement candidates for annotation.

    Pool = top-*depth* from each ranker + every BM25 sweep point + *depth*
    seeded random chunks per query, de-duplicated to ``(query_id, chunk_id)``
    rows. The seed is fixed so pools are reproducible.

    TODO(Tanchhay): implement pooling.
    """

    raise NotImplementedError("TODO(Tanchhay): implement build_pool")
