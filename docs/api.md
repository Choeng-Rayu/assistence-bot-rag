# API

The FastAPI service mirrors the shipped `rayu-web` support bot. Responses to
the chat endpoint are newline-delimited JSON (`application/x-ndjson`).

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | `status`, `index_version`, `chunk_count`, `ranker`, `llm_mode` |
| `POST` | `/api/support-chat` | Streaming chat (NDJSON, contract below) |
| `GET` | `/api/docs` | Document metadata list |
| `GET` | `/api/retrieve?q=&k=&ranker=` | Debug retrieval, only when `RAYU_RAG_DEBUG=1` |
| `GET` | `/` and `/static/*` | Frontend |

## Chat request

```json
{"messages": [{"role": "user", "content": "How do I install?"}]}
```

1–12 turns, each 1–2,000 chars, ≤8,000 chars total, last turn must be `user`.

## NDJSON event order

```
{"type":"sources","sources":[{"title":"Installation","url":"/docs/01-installation"}]}
{"type":"delta","text":"Run the installer: "}
{"type":"delta","text":"```bash\ncurl ...\n```"}
{"type":"done"}
```

Sources are emitted once, up to 4 unique URLs, before any delta. Deltas follow
in order. `done` terminates the stream.

## Errors

Every error is a JSON envelope:

```json
{"error": "rate_limited", "message": "Too many requests; try again shortly."}
```

| Code | Meaning |
|---|---|
| `invalid_request` | Body/shape/limits/message-order failure |
| `forbidden_origin` | `Origin` not allowed |
| `rate_limited` | Per-IP or global budget exhausted |
| `not_configured` | Gateway mode without `RAYU_BOT_API_KEY` |
| `upstream_auth` | Gateway rejected the key |
| `capacity` | Upstream capacity exhausted |
| `busy` | Transient upstream concurrency limit |
| `upstream` | Any other upstream failure |

Pre-stream failures use the envelope with an HTTP error status. Failures after
streaming starts are emitted as `{"type":"error","code":...,"message":...}`.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `RAYU_BOT_API_KEY` | — | Server-only gateway key (never exposed) |
| `RAYU_BOT_MODEL` | `deepseek-v4.1-flash-cloud` | Chat model id |
| `RAYU_BOT_GATEWAY_URL` | `https://gateway.rayucode.com` | LLM gateway base URL |
| `RAYU_RAG_LLM` | `mock` | `mock` or `gateway` |
| `RAYU_RAG_RANKER` | `keyword` | Default ranker |
| `RAYU_RAG_REFUSAL_THRESHOLD` | unset | Score threshold; unset disables it |
| `RAYU_RAG_DEBUG` | `0` | Enable `/api/retrieve` when `1` |
| `RAYU_DOCS_SITE_BASE` | `https://rayucode.com` | Base URL for doc links |
| `RAYU_DOCS_SOURCE_COMMIT` | pinned commit | Corpus provenance |
| `RAYU_BOT_IP_WINDOW_LIMIT` | `6` | Requests per IP per window |
| `RAYU_BOT_IP_WINDOW_MINUTES` | `10` | Window length |
| `RAYU_BOT_IP_DAILY_LIMIT` | `50` | Requests per IP per UTC day |
| `RAYU_BOT_GLOBAL_DAILY_LIMIT` | `500` | Process-wide requests per UTC day |
