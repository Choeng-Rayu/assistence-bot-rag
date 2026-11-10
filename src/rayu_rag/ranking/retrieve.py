"""Shared retrieval pipeline used by the API, CLI, and evaluation harness.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, Ranker, RetrievalResult

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

    Behaviour to implement:

    * delegate scoring to ``ranker.rank(query, index, k=k)``;
    * keep at most *k* hits and at most *budget_chars* total chunk characters
      (stop before the first hit that would exceed the budget);
    * set ``refused`` when the best score is below *threshold* (``None`` means
      never refuse, and an empty hit list also refuses);
    * an empty postings match is a normal empty result, never an error;
    * when the index artifact is missing/unusable, retry over ``chunks.jsonl``
      with the keyword fallback and set ``used_fallback=True``;
    * ``normalized_terms`` and ``diagnostics`` report the tokenizer output and
      the applied ``k``/``budget_chars``/``threshold``/``ranker``.

    TODO(Tanchhay): implement the retrieval pipeline and budget/refusal logic.
    """

    raise NotImplementedError("TODO(Tanchhay): implement retrieve")
