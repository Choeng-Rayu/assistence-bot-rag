"""Render evaluation reports as Markdown.

Owner: Tanchhay.
"""

from __future__ import annotations

__all__ = ["to_markdown"]


def to_markdown(report: dict) -> str:
    """Render an evaluation report dict as a Markdown document.

    Sections: run metadata (ranker, split, corpus version), an aggregate
    metrics table with bootstrap CIs, a per-query table, and a short notes
    section (pool-relative recall, kappa if available).
    """

    meta = report["meta"]
    lines = [
        "# Evaluation report",
        "",
        f"- Ranker: `{meta['ranker']}`",
        f"- Split: `{meta['split']}`",
        f"- Corpus version: `{meta['corpus_version']}`",
        f"- Queries: {meta['query_count']} ({meta['scored_query_count']} with relevant judgements)",
        f"- Bootstrap: {meta['bootstrap_resamples']} resamples, seed {meta['bootstrap_seed']}, 95% CI",
        "",
        "## Aggregate metrics",
        "",
        "| Metric | Mean | 95% CI |",
        "|---|---|---|",
    ]
    for name, stats in report["aggregate"].items():
        lines.append(f"| {name} | {stats['mean']:.3f} | [{stats['ci_low']:.3f}, {stats['ci_high']:.3f}] |")

    metric_names = list(report["aggregate"])
    lines += ["", "## Per query", "", "| Query | Category | " + " | ".join(metric_names) + " | Top hit |"]
    lines.append("|---|---|" + "---|" * (len(metric_names) + 1))
    for row in report["per_query"]:
        top = row["retrieved"][0] if row["retrieved"] else "-"
        if row["judged"]:
            cells = " | ".join(f"{row['metrics'][name]:.3f}" for name in metric_names)
        else:
            cells = " | ".join("n/a" for _ in metric_names)
        lines.append(f"| {row['query_id']} | {row['category']} | {cells} | `{top}` |")

    kappa = report.get("kappa")
    lines += [
        "",
        "## Notes",
        "",
        "- Recall is pool-relative: the denominator is the relevant set found in the judged pool.",
        "- Binary relevance for P/R/MRR/MAP is grade >= " + str(meta["relevant_grade"]) + "; NDCG uses graded gains 2^grade - 1.",
        "- Queries without relevant judgements (adversarial/unanswerable) are excluded from aggregates.",
    ]
    if kappa is not None:
        lines.append(f"- Cohen's kappa: {kappa:.3f}" + (" (below 0.5: binary relevance fallback)" if kappa < 0.5 else ""))
    return "\n".join(lines) + "\n"
