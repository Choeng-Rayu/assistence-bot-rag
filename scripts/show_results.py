"""Print a human-readable demo of the ranking and evaluation work (Tanchhay).

Run: python scripts/show_results.py
"""

from __future__ import annotations

from pathlib import Path

from rayu_rag.config import Config
from rayu_rag.evaluation import evaluate
from rayu_rag.evaluation.harness import load_queries
from rayu_rag.indexing import load_index
from rayu_rag.ranking import build_ranker, retrieve

RANKERS = ("keyword", "tfidf", "bm25", "fusion")
DEMO_QUERIES = (
    "what does a 429 error mean",
    "how do I install rayu with one command",
    "who pays for a team member's requests",
    "how do I deploy rayu to kubernetes",
)


def banner(text: str) -> None:
    print("\n" + "=" * 78 + f"\n{text}\n" + "=" * 78)


def main() -> None:
    config = Config.from_env()
    index = load_index(config.index_dir)

    banner("1. SEARCH DEMO: top 3 chunks per ranker")
    for query in DEMO_QUERIES:
        print(f"\nQuestion: {query!r}")
        for name in RANKERS:
            result = retrieve(query, index, build_ranker(name), k=3)
            top = ", ".join(f"{h.chunk.chunk_id} ({h.score:.2f})" for h in result.hits) or "(no results)"
            print(f"  {name:8s} -> {top}")

    banner("2. EVALUATION: all rankers, dev and test split")
    print(f"{'split':5s} {'ranker':8s} {'P@1':>6s} {'P@5':>6s} {'R@5':>6s} {'MRR@10':>7s} {'MAP':>6s} {'NDCG@5':>7s} {'NDCG@10':>8s}")
    for split in ("dev", "test"):
        for name in RANKERS:
            agg = evaluate(ranker=name, split=split, config=config)["aggregate"]
            cells = " ".join(f"{agg[m]['mean']:{w}.3f}" for m, w in
                             (("P@1", 6), ("P@5", 6), ("R@5", 6), ("MRR@10", 7), ("MAP", 6), ("NDCG@5", 7), ("NDCG@10", 8)))
            print(f"{split:5s} {name:8s} {cells}")

    banner("3. WHERE FUSION FAILS ON THE TEST SPLIT (P@1 = 0)")
    queries = {q["query_id"]: q for q in load_queries(Path("eval/queries.jsonl"))}
    report = evaluate(ranker="fusion", split="test", config=config)
    for row in report["per_query"]:
        if row["judged"] and row["metrics"]["P@1"] == 0.0:
            print(f"  {row['query_id']} {queries[row['query_id']]['query']!r}")
            print(f"      expected: {', '.join(row['relevant'])}")
            print(f"      got:      {row['retrieved'][0]}")

    banner("4. REFUSAL: adversarial and unanswerable queries")
    ranker = build_ranker("bm25")
    for q in queries.values():
        if q["category"] in ("adversarial", "unanswerable"):
            hits = retrieve(q["query"], index, ranker, k=1).hits
            best = f"{hits[0].score:.2f}" if hits else "none"
            print(f"  [{q['category']:12s}] {q['query']!r}: best BM25 score {best}")
    print("\n  (No refusal threshold is set yet; that calibration belongs to Reach.)")

    banner("DONE: full tables are in reports/<ranker>-<split>/eval.md")


if __name__ == "__main__":
    main()
