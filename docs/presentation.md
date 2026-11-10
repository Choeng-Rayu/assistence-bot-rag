# Presentation outline and demo runbook

Nine slides, one clear owner each. Speaker notes are the bullets under each
slide.

## Slide 1 — Introduction and problem (Rayu)

- RayuCode ships a support bot with hand-tuned keyword retrieval: no index, no
  term weighting, no evaluation.
- Goal: a docs-only RAG assistant with measured retrieval quality and grounded,
  cited answers.
- Scope: 14 frozen docs, Python + stdlib IR, FastAPI, open evaluation.

## Slide 2 — Baseline and why measure (Rayu + Tanchhay)

- The baseline is an exact port of `scoreSection()` (3/2 weights, caps, scale).
- Without labelled queries and an evaluation harness we cannot tell whether a
  new ranker is better.
- Everything is compared on the same 40-query dev split with bootstrap CIs.

## Slide 3 — Corpus and chunking (Nike)

- 14 Markdown docs copied from a pinned commit; manifest stores SHA-256.
- Heading-aware chunks of ≤1,800 chars, code fences never split.
- Stable chunk ids `slug#heading~n` keep citations valid across rebuilds.

## Slide 4 — Tokenizer, inverted index, Boolean (Somnang)

- Shared tokenizer: NFKC, lowercase, stopwords keeping negations, light stem.
- Identifiers are kept whole **and** split (`deepseek-v4.1-flash-cloud`, `429`).
- Sorted postings give linear-merge AND/OR/NOT: demo
  `boolean '429 AND NOT hosted'`.

## Slide 5 — TF-IDF vs BM25 sweep (Tanchhay)

- TF-IDF/cosine is the evaluation baseline.
- BM25 adds length normalization; sweep `k1 in {0.9,1.2,1.5}`,
  `b in {0,0.75,1}` on dev.
- Report the chosen parameters and the dev gain, then the one hold-out result.

## Slide 6 — Evaluation design and results (Tanchhay)

- 60 queries: 40 paraphrase, 10 adversarial, 10 identifier/negation.
- Graded qrels 0–3, two annotators, Cohen's kappa; pooled candidates.
- P@1/P@5/R@5/MRR/MAP/NDCG with 95% bootstrap CIs; 40/20 dev/test.

## Slide 7 — RAG prompt, citations, refusal (Reach)

- One system message with canonical facts and `<docs id=... source=...>` blocks.
- Data-not-instructions rule mitigates prompt injection.
- `sources -> delta -> done` NDJSON; ≤4 pills; explicit refusal when ungrounded.

## Slide 8 — Live demo (Reach presents, Rayu drives)

- `RAYU_RAG_LLM=mock python -m rayu_rag serve --port 8000`.
- Ask an answerable question, show streaming and citations.
- Ask an unanswerable question, show refusal. Show `/api/health`.

## Slide 9 — Lessons, limits, roadmap (Rayu)

- Lessons: disjoint ownership and frozen contracts enabled parallel work;
  deterministic artifacts made regressions visible.
- Limits: docs-only corpus, keyword/BM25 only, English-focused.
- Deferred: web crawl and web-only queries, vectors, LLM reranking, Khmer.

## Demo runbook

```bash
source .venv/bin/activate
pytest -q
python -m rayu_rag prepare && python -m rayu_rag build-index
python -m rayu_rag verify
RAYU_RAG_LLM=mock python -m rayu_rag serve --port 8000 &
curl -sN -X POST http://127.0.0.1:8000/api/support-chat \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"How do I install on Windows?"}]}'
```

Open <http://127.0.0.1:8000/> to show streaming, source pills, refusal, and the
stop button.
