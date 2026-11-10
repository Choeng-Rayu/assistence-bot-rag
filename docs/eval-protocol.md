# Evaluation protocol

The harness scores any ranker with one command and reports retrieval quality
with confidence intervals, plus a separate answer-level check.

## Query set

A 60-query docs-only set:

- 40 paraphrase queries (natural user wording),
- 10 adversarial queries (prompt-injection / off-topic attempts),
- 10 hard identifier/negation queries (`429`, `rayu_sk_live_...`,
  `deepseek-v4.1-flash-cloud`, `not hosted`, ...).

A separate 12-query seed set (8 dev / 4 test) is used for smoke tests. The
proposal's 10 web-only queries are deferred (`queries.deferred.web.jsonl`).

## Splits

Split 40 dev / 20 held-out test. Parameters (`k1`, `b`, fusion `alpha`,
refusal threshold) are tuned **only** on dev; the hold-out is reported once and
never used for selection.

## Qrels

Graded relevance 0–3 per `(query_id, chunk_id)`:

| Grade | Meaning |
|---|---|
| 3 | Directly answers the question |
| 2 | Relevant and supports the answer |
| 1 | Mentions the topic but does not answer |
| 0 | Not relevant |

Two annotators judge independently; disagreements are adjudicated. Cohen's
kappa is reported; if kappa < 0.5, fall back to binary relevance and say so.

## Pooling

Candidates per query = top-10 from each ranker + every BM25 sweep point
(`k1 in {0.9, 1.2, 1.5}` x `b in {0, 0.75, 1}`) + 5 seeded random chunks.
Deduplicate to `(query_id, chunk_id)` and judge the pool. Recall is therefore
**pool-relative**: the denominator is the relevant set found in the pool.

## Metrics

Binary relevance for ranking metrics is `grade >= 2`.

```
P@k     = |relevant ∩ top_k| / k
R@k     = |relevant ∩ top_k| / |relevant|
F1@k    = 2PR / (P + R)
RR      = 1 / rank(first relevant), else 0
AP      = (sum over relevant hits of P@rank) / |relevant|
DCG@k   = sum_{i=1..k} (2^grade_i - 1) / log2(i + 1)
NDCG@k  = DCG@k / IDCG@k
```

Report P@1, P@5, R@5, MRR@10, MAP, NDCG@5 and NDCG@10.

## Bootstrap

Percentile bootstrap over query-level metric values: 1,000 resamples, seed 13,
95% interval. For candidate minus baseline use a paired bootstrap over the
per-query differences.

## Report format

`reports/eval.json` contains `meta` (ranker, split, corpus_version, timestamp
policy), `aggregate` (mean + CI per metric) and `per_query` rows. `reports/eval.md`
renders the same as a Markdown table plus notes on pool-relative recall and
kappa. Answer-level results go to `reports/answer-eval.json` with targets:
citation correctness ≥85%, abstention ≥90%, completeness ≥80%, plus a
human spot-check of 10 answers.
