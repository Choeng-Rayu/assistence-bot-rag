# Architecture

A docs-only RAG support assistant. Offline, a frozen Markdown corpus becomes a
deterministic chunk store and inverted index. Online, a browser talks to a
FastAPI service that retrieves chunks, checks refusal, builds a grounded prompt,
streams the model answer, and returns citations.

## Offline / online flow

```
OFFLINE (deterministic)
  rayu-web/public/docs/*.md
        |  copy once (scripts/copy_docs.sh)
        v
  data/docs/*.md --prepare--> artifacts/corpus/{documents,chunks}.jsonl
        |                              + artifacts/index/manifest.json
        v
  tokenize --build-index--> artifacts/index/index.json
                             {postings (sorted), doc_lengths, avgdl, ids}

ONLINE
  browser (web/) --POST /api/support-chat (NDJSON)-->
        |
        v
  validate -> origin -> rate limit
        |
        v
  retrieval query (last 2 user turns, <=600 chars)
        |
        v
  Ranker: BM25 primary (+ keyword fusion / identifier boost)
        |
        v
  top-5 chunks, <=6,000 chars -> refusal check -> prompt assembly
        |
        v
  OpenAI-compatible gateway (SSE) -> relay as NDJSON: sources, delta..., done
```

## Module boundaries

| Package | Owner | Responsibility |
|---|---|---|
| `contracts.py`, `config.py`, `io.py`, `cli.py` | Rayu | Frozen types, environment config, canonical JSON/JSONL, command wiring |
| `corpus/` | Nike | Slugging, chunking, document metadata, manifests |
| `indexing/` | Somnang | Tokenizer, postings, Boolean filters, index build/store |
| `ranking/` | Tanchhay | Keyword/TF-IDF/BM25/fusion rankers, retrieval pipeline |
| `evaluation/` | Tanchhay | Metrics, bootstrap CI, κ, pooling, harness, reports |
| `rag/` | Reach | Retrieval query, prompt, LLM client, SSE parsing, citations, refusal |
| `api/` | Reach | FastAPI app, routes, validation, origin, rate limits |
| `web/` | Reach | Vanilla single-page chat frontend |

Dependency direction is one-way: `api -> rag -> ranking -> indexing -> corpus ->
contracts`. `evaluation` consumes `ranking` and `indexing`. `contracts` imports
no other project module.

## Frozen contracts

| Type | Purpose |
|---|---|
| `DocumentMeta` | One corpus document: slug, title, path/url, sha256, counts |
| `Chunk` | Retrievable, citable unit: id, heading path, url, text, lengths |
| `Posting` | One `(chunk_id, tf)` entry in the inverted index |
| `IndexArtifact` | Serializable index: versions, avgdl, postings, doc lengths |
| `LoadedIndex` | Artifact plus materialized chunks and a `by_id` map |
| `ScoredChunk` | Chunk + score + rank + per-component breakdown |
| `RetrievalResult` | Query terms, hits, refusal and fallback diagnostics |
| `Ranker` (Protocol) | `name` and `rank(query, index, k=10)` |
| `ChatMessage`, `SourceRef`, `Citation` | Conversation and citation values |
| `ChatEvent` | `sources` / `delta` / `done` / `error` TypedDicts |

## Request lifecycle

1. **Validate** — 1–12 turns, each ≤2,000 chars, ≤8,000 total, last turn user.
2. **Origin** — missing `Origin` allowed; otherwise must match `Host` or the
   allowlist.
3. **Rate limit** — per-IP sliding window + daily cap, then global daily cap.
4. **Retrieve** — last 2 user turns (tail-capped at 600 chars); ranker returns
   top hits; trim to 5 chunks / 6,000 chars.
5. **Refuse** — no hits or a top score below the calibrated threshold yields an
   explicit "not in the docs" answer.
6. **Prompt** — one system message (system prompt + canonical facts + `<docs>`
   blocks) followed by the conversation.
7. **Stream** — relay the gateway as NDJSON `sources -> delta... -> done`, or a
   single `error` event.

## Failure behaviour

| Situation | Behaviour |
|---|---|
| Empty postings match | Normal empty result; no exception |
| Score below threshold | `refused=True`; assistant answers that the docs do not cover it |
| Missing/unreadable index | Keyword fallback over `chunks.jsonl`, `used_fallback=True` |
| Missing gateway key | `not_configured` error unless `RAYU_RAG_LLM=mock` |
| Upstream auth failure | `upstream_auth` error, no partial answer |
| Rate limited | `rate_limited` error with retry hint |
| Malformed SSE line | Ignored; the stream continues |
