"""Shared retrieval pipeline used by the API, CLI, and evaluation harness.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, Ranker, RetrievalResult, ScoredChunk
from ..indexing.tokenizer import tokenize
from .keyword import KeywordRanker

__all__ = ["retrieve"]


def retrieve(
    query: str,
    index: LoadedIndex,
    ranker: Ranker,
    k: int = 5,
    budget_chars: int = 6000,
    threshold: float | None = None,
) -> RetrievalResult:
    """Run *ranker* over *index* and trim the result to the API budget.

    * delegates scoring to ``ranker.rank(query, index, k=k)``;
    * keeps at most *k* hits and at most *budget_chars* total chunk characters
      (stops before the first hit that would exceed the budget);
    * sets ``refused`` when the best score is below *threshold* (``None`` means
      never refuse, and an empty hit list always refuses);
    * an empty postings match is a normal empty result, never an error;
    * when the index postings are missing or the ranker fails, retries over the
      loaded chunks with the keyword ranker and sets ``used_fallback=True``;
    * ``normalized_terms`` and ``diagnostics`` report the tokenizer output and
      the applied ``k``/``budget_chars``/``threshold``/``ranker``.
    """

    used_fallback = False
    ranker_name = getattr(ranker, "name", type(ranker).__name__)
    needs_postings = not isinstance(ranker, KeywordRanker)
    hits: list[ScoredChunk]
    if needs_postings and not index.artifact.postings and index.chunks:
        hits, used_fallback = KeywordRanker().rank(query, index, k=k), True
    else:
        try:
            hits = ranker.rank(query, index, k=k)
        except NotImplementedError:
            raise
        except Exception:
            if not index.chunks:
                raise
            hits, used_fallback = KeywordRanker().rank(query, index, k=k), True

    kept: list[ScoredChunk] = []
    used = 0
    for hit in hits[: max(k, 0)]:
        size = hit.chunk.char_len or len(hit.chunk.text)
        if used + size > budget_chars:
            break
        kept.append(hit)
        used += size

    best = kept[0].score if kept else None
    refused = best is None or (threshold is not None and best < threshold)
    return RetrievalResult(
        query=query,
        normalized_terms=tuple(tokenize(query, for_query=True)),
        hits=tuple(kept),
        refused=refused,
        used_fallback=used_fallback,
        diagnostics={
            "ranker": "keyword" if used_fallback else ranker_name,
            "k": k,
            "budget_chars": budget_chars,
            "threshold": threshold,
            "chars_used": used,
            "best_score": best,
        },
    )
