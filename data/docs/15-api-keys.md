# 15. API keys and the Rayu API

This page is for **your own code** calling Rayu-hosted models with a Rayu API
key. One key works across every model your plan allows — you choose the model
on each request.

If you are looking for how to connect an external provider's key (Anthropic,
OpenAI, Google, etc.) to the Rayu CLI, see [Providers](./03-providers.md). That
is a different credential and is not covered here.

## Call Rayu from your own code

Everything you need for the first request: the base URL, the credential header,
and the two wire formats.

| Setting | Value |
|---|---|
| **Model API base URL** | `https://gateway.rayucode.com` |
| **OpenAI-compatible base** | `https://gateway.rayucode.com/v1` |
| **Anthropic-compatible base** | `https://gateway.rayucode.com` |
| **API key format** | `rayu_sk_live_…` |
| **Authentication** | `Authorization: Bearer <key>` or `x-api-key: <key>` |
| **Formats** | OpenAI Chat Completions and Anthropic Messages |
| **Available on** | Pro, Plus, and Max plans |

The **accounts API** lives at `https://api.rayucode.com/api` (dashboard,
billing, key management). Model traffic always goes to
`https://gateway.rayucode.com`; do not send an API key to the accounts API.

## Create an API key

1. Sign in at <https://rayucode.com>.
2. Open **Dashboard → API Keys** (<https://rayucode.com/dashboard/api-keys>).
3. Choose **Generate API Key**, give it a name such as `ci-agent` or
   `production-backend`, and copy the key.

Copy the key once at creation — it is shown **once**, and Rayu stores only a
SHA-256 hash of it. Export it in your shell:

```bash
export RAYU_API_KEY="rayu_sk_live_your_key_here"
```

A lost key cannot be recovered; rotate it or create a replacement instead.

API access is a paid-plan feature. Free and Basic accounts cannot create keys
**on their own plan** — but a **team seat does grant it**: if you belong to a team
whose plan includes API access, you can create keys even on a Free personal plan,
and those keys bill the **team's** credit pool. See
[Subscription plans](./18-subscription-plans.md#team-plans).

### Key controls

A key can be narrower than the account that owns it:

| Control | What it does |
|---|---|
| **Name** | A label for dashboards and usage reports. |
| **Model allowlist** (`allowedModels`) | Empty means every model the plan allows. A non-empty list restricts the key to those model ids. |
| **Credit cap** (`creditLimit`) | Optional per-key credit ceiling per billing period, across every model the key uses. |
| **Rate limit** (`rateLimitRpm`) | Optional requests-per-minute ceiling for this key. |
| **Expiry** (`expiresAt`) | Optional date after which the key stops working. |

You can hold up to **10 active keys**. Rotating a key mints a new secret and
retires the old one; choose a grace window (up to 7 days) if callers cannot be
redeployed at once. Revoking a key takes effect on the next request.

### Store it safely

- Keep the key in an environment variable or secret manager — never in source
  code, `RAYU.md`, settings files, or a commit.
- Use a separate key per application or environment so one can be revoked
  without breaking the others.
- If a key leaks, revoke it immediately and create a replacement.
- Keys act as the owning user with normal user privileges. They cannot call
  admin endpoints.

## One key, many models

A Rayu API key is **account-scoped, not model-scoped**. The same key can call
any model that both your plan and the key's allowlist permit. You select the
model per request with the `model` field — there is no separate key, token, or
endpoint per model.

| What you want | How to do it |
|---|---|
| Use every model on your plan | Create the key without a model allowlist. |
| Restrict a key to a few models | Set `allowedModels` when creating or editing the key. |
| Change models between requests | Send a different `model` id to the same endpoint. |
| Discover what a key may call | `GET /v1/models` with that key. |
| Widen or narrow access later | Edit the key's allowlist in the dashboard; changes apply immediately. |

`GET /v1/models` returns the **intersection** of your plan's catalog and the
key's allowlist. A key with no allowlist sees the whole plan catalog; a scoped
key sees only its own models. A model outside the allowlist returns `403` — even
if the plan includes it.

### Example: one key, three models

The same chat request in three languages, each selecting a different model
with the same key. Only the `model` value changes.

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4.1-flash-cloud",
    "messages": [{"role": "user", "content": "Summarize this error log."}]
  }'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="longcat-2.5",
    messages=[{"role": "user", "content": "Summarize this 400-page PDF."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "us.anthropic.claude-sonnet-4-6",
  messages: [{ role: "user", content: "Review this design." }],
});

console.log(response.choices[0].message.content);
```

Model ids must match an `id` from `GET /v1/models` exactly. Short aliases such
as `sonnet` or `opus` are **not** accepted by the API.

### Example: route by role with one key

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

MODELS = {
    "fast": "deepseek-v4.1-flash-cloud",
    "long_context": "longcat-2.5",
    "review": "us.anthropic.claude-sonnet-4-6",
}

def complete(prompt: str, role: str = "fast") -> str:
    response = client.chat.completions.create(
        model=MODELS[role],
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

This is the entire multi-model design: **one credential, model chosen per
request**. Rayu does not expose a separate auto-router endpoint; if you want
fallback or cost-based routing, implement it in your client with the same key.

```python
import openai

def complete_with_fallback(prompt: str) -> str:
    for model in MODELS.values():
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except openai.APIStatusError:
            continue
    raise RuntimeError("all models failed")
```

## Discover models

`GET /v1/models` returns the models the calling key may use, in OpenAI list
shape.

```bash
curl https://gateway.rayucode.com/v1/models \
  -H "Authorization: Bearer $RAYU_API_KEY"
```

The response is an OpenAI-style list:

```json
{
  "object": "list",
  "data": [
    {
      "id": "deepseek-v4.1-flash-cloud",
      "object": "model",
      "created": 1700000000,
      "owned_by": "rayu",
      "label": "Deepseek-v4.1-flash",
      "description": "Fast general-purpose model",
      "supportsReasoning": true,
      "supportsImage": true,
      "supportsTools": true,
      "contextWindow": 1000000
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `id` | The exact value to send as `model`. |
| `label` | Human-readable display name. |
| `description` | Admin-authored guidance for choosing the model. |
| `supportsReasoning` | Model can emit hidden reasoning. |
| `supportsImage` | Model accepts image input. |
| `supportsTools` | Model supports tool/function calling. |
| `contextWindow` | Maximum context in tokens, or `null` if unset. |

Use this endpoint at runtime instead of hardcoding a catalog — model ids,
availability, and per-plan access can change.

### Current hosted chat catalog

Snapshot taken from production on **3 November 2026**. What `GET /v1/models`
returns for your key depends on your plan and its allowlist; this table is for
orientation only.

| Model id | Label | Context | Reasoning | Images | Tools | Example |
|---|---|--:|:--:|:--:|:--:|---|
| `longcat-2.5` | Long Cat 2.5 | 1M | yes | yes | yes | [Review](#longcat-25) |
| `deepseek-v4.1-flash-1017-cloud` | DeepSeek-V4.1-flash | 1M | yes | yes | yes | [Review](#deepseek-v41-flash-1017-cloud) |
| `mistral-large-4-cloud` | Mistral-large-4 | 1M | yes | yes | yes | [Review](#mistral-large-4-cloud) |
| `qwen3.8-flash` | Qwen3.8-flash | 1M | yes | yes | yes | [Review](#qwen38-flash) |
| `minimax-m3.1-flash-cloud` | Minimax-m3.1-flash | 1M | yes | yes | yes | [Review](#minimax-m31-flash-cloud) |
| `kimi-k3.1-pro` | Kimi-k3.1-pro | 1M | yes | yes | yes | [Review](#kimi-k31-pro) |
| `kimi-for-coding` | kimi-k2.8-for-coding | 1M | yes | yes | yes | [Review](#kimi-for-coding) |
| `longcat-2` | Long Cat 2.0 | 1M | yes | yes | yes | [Review](#longcat-2) |
| `deepseek-v4.1-flash-cloud` | Deepseek-v4.1-flash | 1M | yes | yes | yes | [Review](#deepseek-v41-flash-cloud) |
| `glm-5.3-flash-cloud` | GLM5.3 flash | 1M | yes | no | yes | [Review](#glm-53-flash-cloud) |
| `glm-5.3-cloud` | GLM-5.3 | 1M | yes | no | yes | [Review](#glm-53-cloud) |
| `us.anthropic.claude-sonnet-4-6` | Sonnet 4.6 | 1M | yes | yes | yes | [Review](#usanthropicclaude-sonnet-4-6) |
| `minimax-m3` | Minimax-M3 | 1M | yes | yes | yes | [Review](#minimax-m3) |
| `kimi-k2.7` | Kimi-k2.7-code | 256K | yes | yes | yes | [Review](#kimi-k27) |
| `glm-5.2` | GLM-5.2 | 1M | yes | no | yes | [Review](#glm-52) |
| `qwen3.8-max` | Qwen3.8-max | 1M | yes | yes | yes | [Review](#qwen38-max) |
| `us.anthropic.claude-opus-4-6` | Opus 4.6 | 1M | yes | yes | yes | [Review](#usanthropicclaude-opus-4-6) |
| `poolside-laguna-s-2.1-free` | Laguna-s-2.1 | 262K | yes | yes | yes | [Review](#poolside-laguna-s-21-free) |
| `openai-gpt-oss-20b` | Free | 200K | yes | no | yes | [Review](#openai-gpt-oss-20b) |
| `stepfun-ai-step-3.7-flash` | Step-3.7-flash | 256K | yes | yes | yes | [Review](#stepfun-ai-step-37-flash) |
| `openai-gpt-oss-120b` | GPT-OSS-120b | 200K | yes | no | yes | [Review](#openai-gpt-oss-120b) |
| `nvidia-nemotron-3-ultra-550b-a55b` | Nemotron-3-Ultra-550b-a55b | 1M | yes | yes | yes | [Review](#nvidia-nemotron-3-ultra-550b-a55b) |
| `nvidia-nemotron-3-super-120b-a12b` | Nemotron-3-Super-120b-a12b | 1M | yes | yes | yes | [Review](#nvidia-nemotron-3-super-120b-a12b) |

Click **Review** on any row to jump to that model's runnable example.

### Per-model examples

Each block below uses the same `RAYU_API_KEY` and changes only the `model`
field. Vision-capable models (Images: **yes**) also accept images as base64
`data:` URIs; the models marked **no** return `400` on image input. A model your
plan or key allowlist does not permit returns `403`.

#### `longcat-2.5`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"longcat-2.5","messages":[{"role":"user","content":"Summarize this release note."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="longcat-2.5",
    messages=[{"role": "user", "content": "Summarize this release note."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "longcat-2.5",
  messages: [{ role: "user", content: "Summarize this release note." }],
});

console.log(response.choices[0].message.content);
```

#### `deepseek-v4.1-flash-1017-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4.1-flash-1017-cloud","messages":[{"role":"user","content":"Hello!"}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="deepseek-v4.1-flash-1017-cloud",
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "deepseek-v4.1-flash-1017-cloud",
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(response.choices[0].message.content);
```

#### `mistral-large-4-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral-large-4-cloud","messages":[{"role":"user","content":"Draft a migration plan for this schema."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="mistral-large-4-cloud",
    messages=[{"role": "user", "content": "Draft a migration plan for this schema."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "mistral-large-4-cloud",
  messages: [{ role: "user", content: "Draft a migration plan for this schema." }],
});

console.log(response.choices[0].message.content);
```

#### `qwen3.8-flash`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.8-flash","messages":[{"role":"user","content":"Translate this changelog to English."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="qwen3.8-flash",
    messages=[{"role": "user", "content": "Translate this changelog to English."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "qwen3.8-flash",
  messages: [{ role: "user", content: "Translate this changelog to English." }],
});

console.log(response.choices[0].message.content);
```

#### `minimax-m3.1-flash-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3.1-flash-cloud","messages":[{"role":"user","content":"Extract the action items from this ticket."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="minimax-m3.1-flash-cloud",
    messages=[{"role": "user", "content": "Extract the action items from this ticket."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "minimax-m3.1-flash-cloud",
  messages: [{ role: "user", content: "Extract the action items from this ticket." }],
});

console.log(response.choices[0].message.content);
```

#### `kimi-k3.1-pro`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-k3.1-pro","messages":[{"role":"user","content":"Refactor this function for readability."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="kimi-k3.1-pro",
    messages=[{"role": "user", "content": "Refactor this function for readability."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "kimi-k3.1-pro",
  messages: [{ role: "user", content: "Refactor this function for readability." }],
});

console.log(response.choices[0].message.content);
```

#### `kimi-for-coding`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-for-coding","messages":[{"role":"user","content":"Find the bug in this stack trace."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="kimi-for-coding",
    messages=[{"role": "user", "content": "Find the bug in this stack trace."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "kimi-for-coding",
  messages: [{ role: "user", content: "Find the bug in this stack trace." }],
});

console.log(response.choices[0].message.content);
```

#### `longcat-2`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"longcat-2","messages":[{"role":"user","content":"Summarize this incident report."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="longcat-2",
    messages=[{"role": "user", "content": "Summarize this incident report."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "longcat-2",
  messages: [{ role: "user", content: "Summarize this incident report." }],
});

console.log(response.choices[0].message.content);
```

#### `deepseek-v4.1-flash-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4.1-flash-cloud","messages":[{"role":"user","content":"Hello!"}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="deepseek-v4.1-flash-cloud",
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "deepseek-v4.1-flash-cloud",
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(response.choices[0].message.content);
```

#### `glm-5.3-flash-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.3-flash-cloud","messages":[{"role":"user","content":"Explain this SQL query."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="glm-5.3-flash-cloud",
    messages=[{"role": "user", "content": "Explain this SQL query."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "glm-5.3-flash-cloud",
  messages: [{ role: "user", content: "Explain this SQL query." }],
});

console.log(response.choices[0].message.content);
```

#### `glm-5.3-cloud`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.3-cloud","messages":[{"role":"user","content":"Write unit tests for this function."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="glm-5.3-cloud",
    messages=[{"role": "user", "content": "Write unit tests for this function."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "glm-5.3-cloud",
  messages: [{ role: "user", content: "Write unit tests for this function." }],
});

console.log(response.choices[0].message.content);
```

#### `us.anthropic.claude-sonnet-4-6`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"us.anthropic.claude-sonnet-4-6","messages":[{"role":"user","content":"Review this pull request."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="us.anthropic.claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Review this pull request."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "us.anthropic.claude-sonnet-4-6",
  messages: [{ role: "user", content: "Review this pull request." }],
});

console.log(response.choices[0].message.content);
```

#### `minimax-m3`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3","messages":[{"role":"user","content":"Condense this meeting transcript."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="minimax-m3",
    messages=[{"role": "user", "content": "Condense this meeting transcript."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "minimax-m3",
  messages: [{ role: "user", content: "Condense this meeting transcript." }],
});

console.log(response.choices[0].message.content);
```

#### `kimi-k2.7`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-k2.7","messages":[{"role":"user","content":"Explain this diff."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="kimi-k2.7",
    messages=[{"role": "user", "content": "Explain this diff."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "kimi-k2.7",
  messages: [{ role: "user", content: "Explain this diff." }],
});

console.log(response.choices[0].message.content);
```

#### `glm-5.2`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.2","messages":[{"role":"user","content":"Summarize this RFC."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="glm-5.2",
    messages=[{"role": "user", "content": "Summarize this RFC."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "glm-5.2",
  messages: [{ role: "user", content: "Summarize this RFC." }],
});

console.log(response.choices[0].message.content);
```

#### `qwen3.8-max`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.8-max","messages":[{"role":"user","content":"Analyze this dataset schema."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="qwen3.8-max",
    messages=[{"role": "user", "content": "Analyze this dataset schema."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "qwen3.8-max",
  messages: [{ role: "user", content: "Analyze this dataset schema." }],
});

console.log(response.choices[0].message.content);
```

#### `us.anthropic.claude-opus-4-6`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"us.anthropic.claude-opus-4-6","messages":[{"role":"user","content":"Design a caching strategy for this service."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="us.anthropic.claude-opus-4-6",
    messages=[{"role": "user", "content": "Design a caching strategy for this service."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "us.anthropic.claude-opus-4-6",
  messages: [{ role: "user", content: "Design a caching strategy for this service." }],
});

console.log(response.choices[0].message.content);
```

#### `poolside-laguna-s-2.1-free`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"poolside-laguna-s-2.1-free","messages":[{"role":"user","content":"Complete this TypeScript function."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="poolside-laguna-s-2.1-free",
    messages=[{"role": "user", "content": "Complete this TypeScript function."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "poolside-laguna-s-2.1-free",
  messages: [{ role: "user", content: "Complete this TypeScript function." }],
});

console.log(response.choices[0].message.content);
```

#### `openai-gpt-oss-20b`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai-gpt-oss-20b","messages":[{"role":"user","content":"Answer this support question."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="openai-gpt-oss-20b",
    messages=[{"role": "user", "content": "Answer this support question."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "openai-gpt-oss-20b",
  messages: [{ role: "user", content: "Answer this support question." }],
});

console.log(response.choices[0].message.content);
```

#### `stepfun-ai-step-3.7-flash`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"stepfun-ai-step-3.7-flash","messages":[{"role":"user","content":"Rewrite this README section."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="stepfun-ai-step-3.7-flash",
    messages=[{"role": "user", "content": "Rewrite this README section."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "stepfun-ai-step-3.7-flash",
  messages: [{ role: "user", content: "Rewrite this README section." }],
});

console.log(response.choices[0].message.content);
```

#### `openai-gpt-oss-120b`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai-gpt-oss-120b","messages":[{"role":"user","content":"Explain this error message."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="openai-gpt-oss-120b",
    messages=[{"role": "user", "content": "Explain this error message."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "openai-gpt-oss-120b",
  messages: [{ role: "user", content: "Explain this error message." }],
});

console.log(response.choices[0].message.content);
```

#### `nvidia-nemotron-3-ultra-550b-a55b`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia-nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"Summarize this legal contract."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="nvidia-nemotron-3-ultra-550b-a55b",
    messages=[{"role": "user", "content": "Summarize this legal contract."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "nvidia-nemotron-3-ultra-550b-a55b",
  messages: [{ role: "user", content: "Summarize this legal contract." }],
});

console.log(response.choices[0].message.content);
```

#### `nvidia-nemotron-3-super-120b-a12b`

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia-nemotron-3-super-120b-a12b","messages":[{"role":"user","content":"Classify this customer feedback."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

response = client.chat.completions.create(
    model="nvidia-nemotron-3-super-120b-a12b",
    messages=[{"role": "user", "content": "Classify this customer feedback."}],
)

print(response.choices[0].message.content)
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const response = await client.chat.completions.create({
  model: "nvidia-nemotron-3-super-120b-a12b",
  messages: [{ role: "user", content: "Classify this customer feedback." }],
});

console.log(response.choices[0].message.content);
```

Any id returned by `GET /v1/models` is valid for your key. If a row's example
returns `403`, the key's allowlist or the plan does not include that model.

## Endpoints

### Chat and models

| Method | Path | Format |
|---|---|---|
| POST | `/v1/chat/completions` | OpenAI Chat Completions (streaming and non-streaming) |
| POST | `/v1/messages` | Anthropic Messages (API-key alias) |
| POST | `/anthropic/v1/messages` | Anthropic Messages (native Rayu route) |
| POST | `/v1/messages/count_tokens` | Anthropic token counting |
| GET | `/v1/models` | Models available to the key — OpenAI list shape |

### Other model surfaces

The same key also works for non-chat modalities. Their catalogs are selected on
`GET /v1/models`:

| Method | Path | Catalog query |
|---|---|---|
| POST | `/v1/images/generations` | `GET /v1/models?modality=image` |
| POST | `/v1/videos/generations` | `GET /v1/models?modality=video` |
| POST | `/v1/audio/transcriptions` | `GET /v1/models?modality=audio&operation=stt_batch` |
| POST | `/v1/audio/speech` | `GET /v1/models?modality=audio&operation=tts_batch` |
| POST | `/v1/ocr` | `GET /v1/models?modality=ocr` |
| POST | `/v1/realtime/ticket` | `GET /v1/models?modality=audio&operation=stt_realtime` |

Chat is the default catalog. `modality=` selects one modality's catalog;
`media=image|video|all` is the older filter that merges the BYO and hosted
generation catalogs. Media generation endpoints are billed per image, per
second, or per page rather than per token; the catalog entry carries its own
pricing unit.

### Account and credit metadata

| Method | Path | Returns |
|---|---|---|
| GET | `/v1/credits` | Plan, used/remaining credits, top-up balance, reset time, and the key's own limits |
| GET | `/v1/credits/topup/quote` | Current top-up price quote |
| GET | `/v1/_whoami` | `{"userId": …, "role": "user"}` |
| GET | `/v1/_entitlements` | Plan, status, allowed models, top-up balance |

These are read-only and free.

## OpenAI SDK

Point the SDK's `base_url` at the versioned gateway root. The same streaming
request in three languages:

```bash
curl https://gateway.rayucode.com/v1/chat/completions \
  -H "Authorization: Bearer $RAYU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4.1-flash-cloud",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com/v1",
)

stream = client.chat.completions.create(
    model="deepseek-v4.1-flash-cloud",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com/v1",
});

const stream = await client.chat.completions.create({
  model: "deepseek-v4.1-flash-cloud",
  messages: [{ role: "user", content: "Hello!" }],
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}
```

### OpenAI request support

Supported: `messages`, `stream`, `max_tokens` / `max_completion_tokens`,
`temperature`, `top_p`, `stop`, `tools` / `tool_choice`, and image content on
vision models. `max_tokens` defaults to `4096` if omitted. Images must be sent
as base64 `data:` URIs; remote `image_url` links are rejected.

Rejected with `400`: `n` greater than `1`, `logprobs`, `top_logprobs`, `seed`,
and `logit_bias`.

Add `"stream_options": {"include_usage": true}` to receive a final usage chunk
while streaming.

## Anthropic SDK

Point the Anthropic SDK at the gateway root — the SDK appends `/v1/messages`
itself. The SDK sends the key as `x-api-key`, which the gateway accepts. The
same request in three languages:

```bash
curl https://gateway.rayucode.com/v1/messages \
  -H "x-api-key: $RAYU_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4.1-flash-cloud",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ["RAYU_API_KEY"],
    base_url="https://gateway.rayucode.com",
)

message = client.messages.create(
    model="deepseek-v4.1-flash-cloud",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)

print(message.content[0].text)
```

```ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.RAYU_API_KEY,
  baseURL: "https://gateway.rayucode.com",
});

const message = await client.messages.create({
  model: "deepseek-v4.1-flash-cloud",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(message.content[0].text);
```

`POST /v1/messages/count_tokens` returns `{"input_tokens": N}` and is free.
The count is an estimate; the response carries `x-rayu-token-count: estimate`.

## Responses, cost, and limits

### What a request costs

The charge is reported differently per surface:

- **Anthropic, non-streaming:** a top-level `rayu` member on the response body.
- **Anthropic, streaming:** the `message_delta` event carries `rayu`.
- **OpenAI:** the standard `usage` block. For streaming, set
  `stream_options.include_usage` to receive the final usage chunk.
- **Anthropic headers:** `x-rayu-credits-used`, `x-rayu-credits-remaining` (or
  `unlimited`), and `x-rayu-topup-balance`.
- **Both surfaces:** `GET /v1/credits` is the authoritative balance.

```json
"rayu": {
  "billableTokens": 2950,
  "tokensPerCredit": 1000,
  "credits": 2.95
}
```

`GET /v1/credits` returns the authoritative balance and also echoes the calling
key's `creditLimit`, `allowedModels`, and `rateLimitRpm`, so you can show the
binding limit rather than guessing.

For the rate math, see
[How tokens are charged](./20-how-token-credit-charge.md).

### Error codes

| Status | Meaning |
|---:|---|
| `400` | Invalid JSON, missing `messages`, unsupported parameter, or a capability the model lacks (for example, image input on a text-only model). |
| `401` | Missing, invalid, revoked, or expired API key. |
| `403` | The model is outside your plan, outside this key's allowlist, or the account is not active. |
| `429` | A limit was reached. See the `reason` field. |
| `503` | The model is temporarily unavailable or the gateway is at capacity; retry after `Retry-After`. |
| `502` | The upstream provider failed. |

A `401` looks like this:

```json
{"error": {"message": "invalid API key", "type": "authentication_error"}}
```

### 429 limit reasons

Every `429` carries a machine-readable `reason`, so handle the one that
actually applies instead of showing a generic "out of credits" message:

```json
{
  "error": {"message": "API key rate limit exceeded", "type": "rate_limit_exceeded"},
  "reason": "api_key_rpm_limit",
  "resetSeconds": 60
}
```

| `reason` | What hit the limit |
|---|---|
| `api_key_rpm_limit` | This key's requests-per-minute cap. `Retry-After: 60`. |
| `api_key_credit_limit` | This key's credit cap for the billing period. `Retry-After: 3600`. |
| `daily_turn_limit` | The plan's daily turn cap. |
| `concurrency` | Too many in-flight requests; transient, retry in about 2 seconds. |
| `requests` | Short-window request rate; retry in about a minute. |
| `period_limit` | The account's credit allowance for the period is exhausted. |
| `weekly_limit` / `session_window_limit` | Plan pacing window reached; credit may remain. |
| `bucket_limit` / `pool_limit` | A team wallet limit. |

Most `429` responses also send `Retry-After`. Some carry an `x-rayu-limit`
header with the same reason. Retry with backoff; do not retry `400` or `403`.

## Security checklist

- Keep keys server-side. Never ship one in a browser, mobile app, or public
  repository.
- Use a distinct key per service and environment.
- Set a model allowlist, credit cap, rate limit, and expiry for untrusted or
  automated callers.
- Rotate on a schedule and after any suspected exposure.
- Revoke immediately from the dashboard if a key leaks.

## Related

- [Subscription plans](./18-subscription-plans.md) — plans that include API access
- [Credits and limits](./19-credits-and-limits.md) — allowances and top-ups
- [How tokens are charged](./20-how-token-credit-charge.md) — per-model credit math
