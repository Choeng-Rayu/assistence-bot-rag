# RayuCode RAG Support Assistant

A docs-only retrieval-augmented support assistant for RayuCode: frozen Markdown
corpus, deterministic inverted index, keyword/TF-IDF/BM25/fusion ranking, a
reusable evaluation harness, and a streaming FastAPI chat API with citations.

> **Status: scaffold.** The project structure, contracts, corpus, CLI, config,
> and test suite are in place, but every member-owned algorithm raises
> `NotImplementedError("TODO(<Owner>): ...")`. Search for `TODO(` to find the
> work assigned to each member. This run is project setup only.

## Quickstart

```bash
cd /home/rayu/Y4/Web-retrieval/assistence-bot-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest -q                       # green skeleton test suite
PYTHONPATH=src python -m rayu_rag --help
```

Once the members have filled in their modules:

```bash
python -m rayu_rag prepare                       # data/docs -> artifacts/corpus
python -m rayu_rag build-index                   # -> artifacts/index
python -m rayu_rag verify
python -m rayu_rag boolean '429 AND NOT hosted'
python -m rayu_rag retrieve "cost per million tokens" --ranker keyword --k 5
python -m rayu_rag eval --ranker keyword --split dev
python -m rayu_rag pool
RAYU_RAG_LLM=mock python -m rayu_rag serve --port 8000
```

CLI commands: `prepare`, `build-index`, `boolean`, `retrieve`, `eval`, `pool`,
`answer-eval`, `verify`, `serve`. All handlers import their implementation
lazily, so `--help` works while modules are still stubs.

## Repository layout

```
assistence-bot-rag/
├── README.md                     this file
├── pyproject.toml                package metadata, deps, pytest config
├── .env.example                  every runtime variable with defaults
├── data/
│   ├── docs/                     14 frozen Markdown docs + provenance README
│   └── aliases.json              curated synonym map
├── artifacts/                    generated (gitignored)
├── eval/                         queries, qrels, pools (seed data later)
├── reports/                      generated evaluation reports
├── web/                          minimal vanilla frontend (later)
├── src/rayu_rag/
│   ├── contracts.py              frozen dataclasses (Rayu)
│   ├── config.py, io.py, cli.py  config, canonical IO, CLI (Rayu)
│   ├── corpus/                   chunking + manifest (Nike)
│   ├── indexing/                 tokenizer, postings, Boolean, builder, store (Somnang)
│   ├── ranking/                  keyword, tfidf, bm25, fusion, retrieve (Tanchhay)
│   ├── evaluation/               metrics, bootstrap, agreement, pool, harness (Tanchhay)
│   ├── rag/                      prompt, llm, stream, citations, refusal (Reach)
│   └── api/                      FastAPI app, routes, validation, origin, limits (Reach)
├── scripts/                      copy_docs.sh, check_docs.sh, export_sqlite.py
├── tests/                        foundation tests + scaffold stub tests
└── docs/                         architecture, eval protocol, API, presentation
```

## Ownership

| Owner | Role | Files |
|---|---|---|
| **Rayu** | Integration, foundation, docs | `pyproject.toml`, `src/rayu_rag/{__init__,__main__,cli,config,contracts,io}.py`, `tests/conftest.py`, `tests/fixtures/**`, `tests/test_contracts.py`, `README.md`, `docs/**`, CI, Makefile |
| **Nike** | Corpus and chunking | `data/docs/**`, `scripts/copy_docs.sh`, `scripts/check_docs.sh`, `src/rayu_rag/corpus/**` |
| **Somnang** | Tokenizer and inverted index | `src/rayu_rag/indexing/**`, `data/aliases.json`, `scripts/export_sqlite.py` |
| **Tanchhay** | Ranking and evaluation | `src/rayu_rag/ranking/**`, `src/rayu_rag/evaluation/**`, `eval/**`, `reports/**` |
| **Reach** | RAG, API, frontend | `src/rayu_rag/rag/**`, `src/rayu_rag/api/**`, `web/**`, `.env.example` |

Only Rayu edits `contracts.py` and `cli.py`. Every other file has exactly one
owner. Do not edit another member's files; report interface problems instead.

## How to fill in your module

### Nike — corpus

- [x] `corpus/chunker.py`: GitHub heading slugify, ATX headings outside fences,
      H1 + intro preamble, ≤1,800-char line-boundary splits, `x`/`x-1` de-dup,
      chunk ids `<slug>`, `<slug>#<heading>`, `<slug>#<heading>~2`.
- [x] `corpus/prepare.py`: read `data/docs/*.md`, chunk, write
      `documents.jsonl` + `chunks.jsonl` deterministically.
- [x] `corpus/manifest.py`: provenance + per-file SHA-256; `verify_manifest`
      returns `[]` when valid.
- [x] Add chunk-id stability and manifest tests.

### Somnang — indexing

- [ ] `indexing/tokenizer.py`: NFKC, lowercase, split on non-alphanumeric,
      stopwords keeping `not`/`no`/`without`, light stemming with identifier
      exceptions; index identifiers whole **and** split.
- [ ] `indexing/postings.py`: sorted postings, linear merge `intersect`,
      `union`, `complement`.
- [ ] `indexing/boolean.py`: recursive-descent parser and evaluator.
- [ ] `indexing/builder.py` / `store.py`: byte-stable `index.json` +
      `chunks.jsonl`.
- [ ] Golden tokenizer cases for `rayu_sk_live_...`,
      `deepseek-v4.1-flash-cloud`, `429`.

### Tanchhay — ranking and evaluation

- [x] `ranking/keyword.py`: exact port of `scoreSection()` (constants fixed in
      the module docstring).
- [x] `ranking/tfidf.py`, `bm25.py`, `fusion.py`: baselines and the production
      candidate; tune `k1`/`b`/`alpha` on the dev split only.
- [x] `ranking/retrieve.py`: k and character budget, refusal, fallback.
- [x] `evaluation/*`: metrics, bootstrap CI, κ, pooling, harness, report.
- [x] Add seed queries/qrels under `eval/`, then run `eval --split dev`.
      Tuned on dev only: BM25 `k1=1.2, b=0.75` (grid optimum), fusion `alpha=0.5`
      (`python scripts/tune_rankers.py`). Eval set: 60 queries (40 dev / 20 test) in `eval/`.

### Reach — RAG and API

- [ ] `rag/prompt.py`: retrieval query, `<docs>` blocks, message assembly.
- [ ] `rag/llm.py`, `stream.py`: mock mode + gateway SSE parsing.
- [ ] `rag/citations.py`, `refusal.py`: citation mapping, pills, refusal and
      threshold calibration.
- [ ] `api/*`: FastAPI app, chat NDJSON stream, health, docs, debug retrieve,
      validation, origin, rate limits.
- [ ] `web/`: single-page vanilla chat UI (no build step).

### Rayu — integration

- [ ] Keep `contracts.py` frozen; review every interface change.
- [ ] Wire end-to-end demo and refresh README/docs as modules land.

## Corpus provenance

The 14 documents in `data/docs/` are frozen copies from
`Choeng-Rayu/rayu-web` at commit `486bab47797719a893e6aae9b9363460cd7f9cce`
(copied 2026-11-10, source directory `public/docs/`). `README.md` and
`CHANGELOG.md` from the source were deliberately excluded. See
`data/docs/README` for the freeze policy.

**Note:** the original proposal mentions 13 docs; the source repository ships
14 and they are authoritative — `21-policies` is included. Do not edit the
frozen docs; re-copy from a pinned commit instead.

## Deferred work

- Web crawling (Lab 5) and web-only queries; the proposal's 10 web-only queries
  move to a deferred file.
- Dense/vector retrieval and embedders.
- LLM reranking and live corpus refresh.
- Khmer-language retrieval.

## Documentation

- `docs/architecture.md` — offline/online flow, module boundaries, contracts.
- `docs/eval-protocol.md` — query mix, qrels, κ, pooling, metrics, splits.
- `docs/api.md` — endpoints, NDJSON events, error codes, env vars.
- `docs/presentation.md` — 9-slide outline with owners and speaker notes.
