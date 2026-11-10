# 4. Models

Rayu can have several providers connected at once; this page is about choosing
which model answers — for the main session and for subagents.

## Selecting a model: `/model`

In a session:

```text
/model
```

With the Rayu hosted catalog, an OpenAI-compatible endpoint, Bedrock, Vertex,
or any other multi-model connection, this opens a **searchable picker**:

- **Type to filter** — matches against both the **model id** and the
  **provider** (e.g. `llama`, `deepseek`, or `nvidia deepseek` to narrow by
  both).
- **↑ / ↓** move, **Enter** selects, **Esc** cancels.
- The list aggregates models from **all connected providers** (the Rayu hosted
  catalog pinned at the top when you are signed in), so with many providers you
  can find a model fast instead of scrolling.

Selecting a model from another provider switches the active provider to match.
The choice persists across restarts.

Shortcuts:

```text
/model deepseek-chat        # set directly without opening the picker
/model sonnet               # or an alias (below)
/model show                 # just print the current model and exit
```

```bash
rayu --model deepseek-chat  # or at launch
```

**Aliases.** For Claude-family models Rayu understands shorthand names:
`sonnet`, `opus`, `haiku`, `best`, `opusplan`, and the `opus[1m]` /
`sonnet[1m]` long-context variants. On hosted and other providers the picker
shows plain model ids instead.

## The hosted model catalog

When you are signed in, hosted models come from **Rayu's live catalog** — the
model list, display names, descriptions, capabilities and context windows are
all refreshed when you open `/model`, so a new or renamed model shows up
without any CLI update. The authoritative list is at
<https://rayucode.com/models>; the catalog **may change at any time**.
Your plan determines which models you can use — see
[Subscription plans](./18-subscription-plans.md).

## Hosted model ids (DeepSeek, Qwen, Kimi, and more)

Use a model **id** wherever Rayu accepts a model: `rayu --model deepseek-v4-flash`
at launch, `/model deepseek-v4-flash` in a session or the extension composer,
the `"model"` setting in `~/.rayu/settings.json`, and the `model` field in a
[programmatic API](./15-api-keys.md) request. The label is only for display;
the id is what Rayu sends.

For orientation, here is a snapshot of the hosted catalog (the picker and the
website are authoritative):

| Model id | Label | Context | Thinking | Images |
|----------|-------|---------|----------|--------|
| `deepseek-v4-flash` | DeepSeek V4 Flash | 1M | yes | no |
| `deepseek-v4-pro` | DeepSeek V4 Pro | 1M | yes | no |
| `longcat-2` | LongCat 2.0 | 1M | yes | no |
| `glm-5.2` | GLM-5.2 (Ollama Cloud) | 1M | yes | no |
| `kimi-k2.7` | Kimi K2.7 Code (Ollama Cloud) | 256K | yes | no |
| `qwen3.5-397b` | Qwen3.5 397B (Ollama Cloud) | 256K | yes | no |
| `qwen3.5-122b` | Qwen3.5 122B (Ollama Cloud) | 256K | yes | no |
| `gpt-oss-120b` | GPT-OSS 120B (Ollama Cloud) | 128K | yes | no |
| `minimax-m3` | MiniMax M3 (Ollama Cloud) | 128K | yes | no |
| `llama-4` | Llama 4 (Ollama Cloud) | 128K | no | yes |

Credit rates per model live in [Subscription plans](./18-subscription-plans.md).

## Choose a chat model

Pick instruction/chat models. Non-chat models (base, code-completion,
embedding, OCR) will fail with `404` on the chat endpoint. Examples:

| Use | Avoid |
|-----|-------|
| `meta/llama-3.3-70b-instruct` | `google/codegemma-7b` |
| `deepseek-chat`, `deepseek-reasoner` | `*-embedding`, `bge-*` |
| `deepseek-ai/deepseek-v4-pro` | `*-ocr`, `deplot`, `*-parse` |
| `kimi-k2-*`, `qwen3-*-instruct` | `starcoder2-*`, `*-rerank`, `*-guard` |

Rayu skips non-chat ids when choosing a default model.

### Vision (image) models

Pasted images and images returned by tools are sent to the provider, so any
**vision-capable** model can see them. The hosted catalog publishes which
models do; sending an image to a text-only model fails with a clear error. For
a custom BYOK provider, set image support when you configure it.

### Reasoning models

Models that emit hidden reasoning (DeepSeek's `reasoning_content`, MiniMax/GLM
native thinking, Qwen/`gpt-oss`, o-series) surface their thinking as a separate
block. Reasoning is spent from the same output budget, so give them room.
OpenAI `o1`/`o3`/`o4`/`gpt-5` are handled automatically
(`max_completion_tokens`, no `temperature`).

## Per-agent model routing

The main model answers you; Rayu also spawns **subagents** (background workers
and reviewers). You can route them elsewhere:

- **`/subagent_models [AGENT]`** — set the model for **all** spawned agents, or
  for one named agent (`/model_subagent` and `/subagent_model` remain aliases;
  `/subagent_models show` lists current choices, `/subagent_models default`
  resets). By default each agent uses its built-in model. This is a paid-plan
  feature — Free users get an upgrade notice.
- **`/webfetch_model`** — set the model that summarizes pages fetched with
  WebFetch (defaults to the active provider's model).

When you pick a subagent model from another provider, the selection **pins
that provider to the model**: subagents then talk directly to their provider
while your main session talks to its own — multiple providers in one session,
concurrently. You never type the prefix yourself; the picker encodes it, and
`/subagent_models show` displays it as `model · provider`.

Next: [Configuration →](./05-configuration.md)
