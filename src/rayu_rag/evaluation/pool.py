"""Pooled judgement candidates.

Owner: Tanchhay.
"""

from __future__ import annotations

import random
from pathlib import Path

from ..config import Config
from ..io import read_jsonl

__all__ = ["build_pool"]

POOL_SEED = 13
SWEEP_K1 = (0.9, 1.2, 1.5)
SWEEP_B = (0.0, 0.75, 1.0)


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

    Pool = top-*depth* from each ranker + every BM25 sweep point + *random_per_query*
    seeded random chunks per query, de-duplicated to ``(query_id, chunk_id)``
    rows. The seed is fixed so pools are reproducible. Rows are returned and,
    when *out_path* is given, also written as JSONL.
    """

    from ..indexing import load_index
    from ..io import write_jsonl
    from ..ranking import BM25Ranker, build_ranker

    queries = read_jsonl(Path(queries_path or "eval/queries.jsonl"))
    index = load_index(Path(index_dir or Config.from_env().index_dir))

    systems = {name: build_ranker(name) for name in ("keyword", "tfidf", "bm25", "fusion")}
    for k1 in SWEEP_K1:
        for b in SWEEP_B:
            systems[f"bm25(k1={k1},b={b})"] = BM25Ranker(k1=k1, b=b)

    all_ids = sorted(chunk.chunk_id for chunk in index.chunks)
    rows: list[dict] = []
    for query in queries:
        rng = random.Random(f"{POOL_SEED}:{query['query_id']}")
        sources: dict[str, list[str]] = {}
        for name, system in systems.items():
            for hit in system.rank(query["query"], index, k=depth):
                sources.setdefault(hit.chunk.chunk_id, []).append(name)
        for chunk_id in rng.sample(all_ids, min(random_per_query, len(all_ids))):
            sources.setdefault(chunk_id, []).append("random")
        for chunk_id in sorted(sources):
            rows.append(
                {
                    "query_id": query["query_id"],
                    "query": query["query"],
                    "chunk_id": chunk_id,
                    "sources": sorted(set(sources[chunk_id])),
                    "grade": None,
                }
            )

    if out_path is not None:
        write_jsonl(Path(out_path), rows)
    return rows
