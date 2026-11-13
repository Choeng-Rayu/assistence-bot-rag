"""Tune BM25 k1/b and fusion alpha on the dev split only (Tanchhay)."""

from __future__ import annotations

from pathlib import Path

from rayu_rag.config import Config
from rayu_rag.evaluation.harness import METRICS, RELEVANT_GRADE, load_qrels, load_queries
from rayu_rag.indexing import load_index
from rayu_rag.ranking import BM25Ranker, FusionRanker

K1 = (0.9, 1.2, 1.5)
B = (0.0, 0.75, 1.0)
ALPHA = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)


def score(ranker, index, queries, qrels) -> float:
    values = []
    for row in queries:
        grades = qrels.get(row["query_id"], {})
        relevant = {c for c, g in grades.items() if g >= RELEVANT_GRADE}
        if not relevant:
            continue
        ids = [h.chunk.chunk_id for h in ranker.rank(row["query"], index, k=10)]
        values.append(METRICS["NDCG@10"](ids, relevant, grades))
    return sum(values) / len(values)


def main() -> None:
    index = load_index(Config.from_env().index_dir)
    qrels = load_qrels(Path("eval/qrels.jsonl"))
    dev = [q for q in load_queries(Path("eval/queries.jsonl")) if q["split"] == "dev"]
    best = (-1.0, 1.2, 0.75)
    print("BM25 NDCG@10 (dev)")
    for k1 in K1:
        for b in B:
            s = score(BM25Ranker(k1, b), index, dev, qrels)
            print(f"  k1={k1} b={b}: {s:.4f}")
            if s > best[0] + 1e-12:
                best = (s, k1, b)
    print(f"best BM25: k1={best[1]} b={best[2]} ({best[0]:.4f})")
    top = (-1.0, 0.8)
    print("Fusion NDCG@10 (dev)")
    for alpha in ALPHA:
        s = score(FusionRanker(BM25Ranker(best[1], best[2]), alpha), index, dev, qrels)
        print(f"  alpha={alpha}: {s:.4f}")
        if s > top[0] + 1e-12:
            top = (s, alpha)
    print(f"best fusion alpha={top[1]} ({top[0]:.4f})")


if __name__ == "__main__":
    main()
