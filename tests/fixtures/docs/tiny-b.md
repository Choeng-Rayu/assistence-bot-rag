# Tiny B

Tiny B is the second miniature document. It describes models, credits, and rate-limiting behaviour for the foundation tests.

## Models

The default model is `deepseek-v4.1-flash-cloud`. Pick a model when you start a chat session.

```bash
rayu chat --model deepseek-v4.1-flash-cloud
```

Model choice affects both latency and credit consumption.

## Credits and limits

Each request consumes credits based on prompt and completion tokens. Free plans are capped at a small number of requests per minute.

## Rate limits

The gateway returns HTTP 429 when a client exceeds its window budget. Back off and retry later. A server-side key such as `rayu_sk_live_test` still obeys the same limits.

```text
retry-after: 30
```

That is all Tiny B contains.
