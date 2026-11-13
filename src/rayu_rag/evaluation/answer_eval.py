"""Answer-level evaluation: citations, abstention and completeness.

Owner: Tanchhay.
"""

from __future__ import annotations

from pathlib import Path

from ..config import Config
from ..io import read_jsonl

__all__ = ["evaluate_answers"]

TARGETS = {"citation_correctness": 0.85, "abstention": 0.90, "completeness": 0.80}
UNANSWERABLE = ("adversarial", "unanswerable")


def evaluate_answers(n: int = 30, config: Config | None = None) -> dict:
    """Score up to *n* queries per behaviour and return a report dict.

    Targets: citation correctness >=85%, abstention >=90%, completeness >=80%,
    plus a human spot-check of 10 answers.

    This runs on the retrieval pipeline (the ``rag`` package is not required):
    *citation correctness* is the share of answerable queries whose cited
    (retrieved) chunks include a relevant one, *completeness* the share of
    relevant chunks covered by the retrieved set, and *abstention* the share of
    adversarial/unanswerable queries for which ``retrieve`` refuses. Spot-check
    rows are listed for manual review.
    """

    from ..indexing import load_index
    from ..ranking import build_ranker, retrieve
    from .harness import RELEVANT_GRADE, load_qrels, load_queries

    config = config or Config.from_env()
    index = load_index(config.index_dir)
    ranker = build_ranker(config.ranker)
    qrels = load_qrels(Path("eval/qrels.jsonl"))
    queries = load_queries(Path("eval/queries.jsonl"))

    answerable, abstain = [], []
    for row in queries:
        relevant = {c for c, g in qrels.get(row["query_id"], {}).items() if g >= RELEVANT_GRADE}
        result = retrieve(
            row["query"],
            index,
            ranker,
            k=config.top_k,
            budget_chars=config.budget_chars,
            threshold=config.refusal_threshold,
        )
        ids = {hit.chunk.chunk_id for hit in result.hits}
        if relevant and not result.refused:
            answerable.append((row, relevant, ids))
        elif relevant:
            answerable.append((row, relevant, set()))
        elif row.get("category") in UNANSWERABLE:
            abstain.append((row, result.refused))

    answerable, abstain = answerable[:n], abstain[:n]
    citation = _share(1 for _, rel, ids in answerable if rel & ids)
    completeness = (
        sum(len(rel & ids) / len(rel) for _, rel, ids in answerable) / len(answerable)
        if answerable
        else 0.0
    )
    abstention = _share(1 for _, refused in abstain if refused)
    scores = {
        "citation_correctness": citation / len(answerable) if answerable else 0.0,
        "abstention": abstention / len(abstain) if abstain else 0.0,
        "completeness": completeness,
    }
    return {
        "mode": "retrieval-level",
        "ranker": ranker.name,
        "refusal_threshold": config.refusal_threshold,
        "counts": {"answerable": len(answerable), "abstain": len(abstain)},
        "scores": scores,
        "targets": TARGETS,
        "passed": {name: scores[name] >= target for name, target in TARGETS.items()},
        "spot_check": [row["query_id"] for row, _, _ in answerable[:10]],
    }


def _share(flags) -> int:
    return sum(flags)
