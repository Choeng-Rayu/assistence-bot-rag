"""Ranking and evaluation tests (Tanchhay)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from rayu_rag.contracts import LoadedIndex
from rayu_rag.evaluation import (
    average_precision,
    bootstrap_ci,
    cohens_kappa,
    dcg_at_k,
    f1_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    to_markdown,
)
from rayu_rag.indexing import build_index
from rayu_rag.io import chunk_from_dict, read_jsonl
from rayu_rag.ranking import build_ranker, retrieve

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def index() -> LoadedIndex:
    chunks = tuple(chunk_from_dict(r) for r in read_jsonl(FIXTURES / "tiny_chunks.jsonl"))
    return LoadedIndex(build_index(chunks, {}), chunks, {c.chunk_id: c for c in chunks})


def test_metrics_known_values() -> None:
    retrieved, relevant = ["a", "b", "c", "d"], {"b", "d"}
    assert precision_at_k(retrieved, relevant, 2) == 0.5
    assert recall_at_k(retrieved, relevant, 2) == 0.5
    assert f1_at_k(retrieved, relevant, 2) == 0.5
    assert reciprocal_rank(retrieved, relevant) == 0.5
    assert average_precision(retrieved, relevant) == pytest.approx((1 / 2 + 2 / 4) / 2)
    assert dcg_at_k([3, 2], 2) == pytest.approx(7 + 3 / math.log2(3))
    assert ndcg_at_k(["x", "b"], {"b": 3}, 2) == pytest.approx(1 / math.log2(3))
    assert ndcg_at_k(["b"], {"b": 3}, 1) == 1.0
    assert reciprocal_rank(["z"], relevant) == 0.0
    assert recall_at_k(["a"], set(), 1) == 0.0


def test_bootstrap_is_seeded_and_brackets_mean() -> None:
    values = [0.0, 1.0, 1.0, 0.5, 0.75, 1.0]
    first = bootstrap_ci(values)
    assert first == bootstrap_ci(values)
    assert first[0] <= sum(values) / len(values) <= first[1]
    assert bootstrap_ci([]) == (0.0, 0.0)


def test_cohens_kappa() -> None:
    assert cohens_kappa([0, 1, 2, 3], [0, 1, 2, 3]) == 1.0
    assert cohens_kappa([1, 1, 0, 0], [1, 0, 1, 0]) == 0.0
    with pytest.raises(ValueError):
        cohens_kappa([1], [1, 2])


@pytest.mark.parametrize("name", ["keyword", "tfidf", "bm25", "fusion"])
def test_rankers_find_the_install_chunk(name: str, index: LoadedIndex) -> None:
    hits = build_ranker(name).rank("install the CLI", index, k=3)
    assert hits and hits[0].rank == 1
    assert "tiny-a#install" in [h.chunk.chunk_id for h in hits]
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_unknown_ranker_and_empty_match(index: LoadedIndex) -> None:
    with pytest.raises(ValueError):
        build_ranker("nope")
    assert build_ranker("bm25").rank("zzzzqqqq", index) == []


def test_retrieve_budget_and_refusal(index: LoadedIndex) -> None:
    ranker = build_ranker("bm25")
    result = retrieve("install the CLI", index, ranker, k=5, budget_chars=1)
    assert result.hits == () and result.refused
    full = retrieve("install the CLI", index, ranker, k=2)
    assert len(full.hits) <= 2 and not full.refused
    assert retrieve("install the CLI", index, ranker, threshold=1e9).refused
    assert retrieve("zzzzqqqq", index, ranker).refused


def test_retrieve_falls_back_without_postings(index: LoadedIndex) -> None:
    empty = build_index((), {})
    bare = LoadedIndex(empty, index.chunks, index.by_id)
    result = retrieve("install the CLI", bare, build_ranker("bm25"))
    assert result.used_fallback and result.hits


def test_report_renders() -> None:
    report = {
        "meta": {
            "ranker": "bm25", "split": "dev", "corpus_version": "x", "query_count": 1,
            "scored_query_count": 1, "bootstrap_resamples": 10, "bootstrap_seed": 13,
            "relevant_grade": 2,
        },
        "aggregate": {"P@1": {"mean": 1.0, "ci_low": 1.0, "ci_high": 1.0}},
        "per_query": [
            {"query_id": "Q1", "category": "x", "retrieved": ["a"], "judged": True,
             "metrics": {"P@1": 1.0}},
        ],
    }
    text = to_markdown(report)
    assert "| P@1 | 1.000 |" in text and "pool-relative" in text
    json.dumps(report)
