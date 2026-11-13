"""The evaluation harness entry point.

Owner: Tanchhay.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ..config import Config
from ..io import read_jsonl
from .bootstrap import bootstrap_ci
from .metrics import (
    average_precision,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

__all__ = ["evaluate", "load_qrels", "load_queries"]

RELEVANT_GRADE = 2
RETRIEVAL_DEPTH = 10
BOOTSTRAP_SEED = 13

METRICS: dict[str, tuple] = {
    "P@1": lambda ids, rel, grades: precision_at_k(ids, rel, 1),
    "P@5": lambda ids, rel, grades: precision_at_k(ids, rel, 5),
    "R@5": lambda ids, rel, grades: recall_at_k(ids, rel, 5),
    "MRR@10": lambda ids, rel, grades: reciprocal_rank(ids, rel, 10),
    "MAP": lambda ids, rel, grades: average_precision(ids, rel),
    "NDCG@5": lambda ids, rel, grades: ndcg_at_k(ids, grades, 5),
    "NDCG@10": lambda ids, rel, grades: ndcg_at_k(ids, grades, 10),
}


def load_queries(path: Path) -> list[dict]:
    """Read ``queries.jsonl`` rows (``query_id``, ``query``, ``split``, ``category``)."""

    return read_jsonl(Path(path))


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    """Read ``qrels.jsonl`` into ``{query_id: {chunk_id: grade}}``."""

    qrels: dict[str, dict[str, int]] = defaultdict(dict)
    for row in read_jsonl(Path(path)):
        qrels[row["query_id"]][row["chunk_id"]] = int(row["grade"])
    return dict(qrels)


def evaluate(
    *,
    queries_path: Path | None = None,
    qrels_path: Path | None = None,
    ranker: str = "keyword",
    split: str = "dev",
    bootstrap: int = 1000,
    config: Config | None = None,
    out_dir: Path | None = None,
    **kwargs: object,
) -> dict:
    """Score *ranker* on the requested *split* and return a report dict.

    Loads queries/qrels, runs retrieval per query, computes P@1, P@5, R@5,
    MRR@10, MAP, NDCG@5 and NDCG@10 with bootstrap CIs (1000 resamples, seed
    13), and returns per-query rows plus aggregates. *split* is ``dev``,
    ``test`` or ``all``. Queries with no relevant judgement (adversarial or
    unanswerable) are listed per query but excluded from the aggregates.
    """

    from ..indexing import load_index
    from ..ranking import build_ranker

    if split not in ("dev", "test", "all"):
        raise ValueError(f"split must be dev, test or all, not {split!r}")
    config = config or Config.from_env()
    queries_path = Path(queries_path or "eval/queries.jsonl")
    qrels_path = Path(qrels_path or "eval/qrels.jsonl")

    index = load_index(config.index_dir)
    engine = build_ranker(ranker)
    qrels = load_qrels(qrels_path)
    queries = [q for q in load_queries(queries_path) if split == "all" or q.get("split") == split]

    per_query: list[dict] = []
    for row in queries:
        grades = qrels.get(row["query_id"], {})
        relevant = {cid for cid, grade in grades.items() if grade >= RELEVANT_GRADE}
        ids = [hit.chunk.chunk_id for hit in engine.rank(row["query"], index, k=RETRIEVAL_DEPTH)]
        entry = {
            "query_id": row["query_id"],
            "query": row["query"],
            "category": row.get("category", ""),
            "retrieved": ids,
            "relevant": sorted(relevant),
            "judged": bool(relevant),
        }
        if relevant:
            entry["metrics"] = {name: fn(ids, relevant, grades) for name, fn in METRICS.items()}
        per_query.append(entry)

    scored = [entry for entry in per_query if entry["judged"]]
    aggregate: dict[str, dict[str, float]] = {}
    for name in METRICS:
        values = [entry["metrics"][name] for entry in scored]
        mean = sum(values) / len(values) if values else 0.0
        low, high = bootstrap_ci(values, n=bootstrap, seed=BOOTSTRAP_SEED) if values else (0.0, 0.0)
        aggregate[name] = {"mean": mean, "ci_low": low, "ci_high": high}

    report = {
        "meta": {
            "ranker": ranker,
            "split": split,
            "corpus_version": index.artifact.corpus_version,
            "tokenizer_version": index.artifact.tokenizer_version,
            "query_count": len(per_query),
            "scored_query_count": len(scored),
            "bootstrap_resamples": bootstrap,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "relevant_grade": RELEVANT_GRADE,
        },
        "aggregate": aggregate,
        "per_query": per_query,
    }
    return report
