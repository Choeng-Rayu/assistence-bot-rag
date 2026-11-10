# 3. Providers

A **provider** is where your model requests actually go. Rayu supports two
ways to work:

- **Rayu hosted** — Rayu's curated model catalog, billed to your plan or
  credits. Sign in and it activates itself: no API keys at all. This is the
  default path (see [Quickstart](./02-quickstart.md)).
- **Bring your own key (BYOK)** — connect any of ~30 built-in providers (or
  your own endpoint) with your API key or an OAuth sign-in. Requests go
  **directly to that provider**, and you pay the provider — Rayu never sees
  your key usage.

Both can be configured side by side, and you switch freely with `/model`.

## Rayu hosted

The **Rayu (hosted)** provider is not connected with `/connect` — it registers
itself when you sign in:

- `/login` stores your account session securely on your machine.
- If your plan includes hosted models, the provider is activated automatically
  and hosted models appear pinned at the top of `/model`. Requests are
  authenticated with your account and served by Rayu using its own provider
  accounts.
- The model list, display names and context windows come live from Rayu's
  catalog — a newly added model shows up with no CLI update. Pricing follows
  your plan; see [Subscription plans](./18-subscription-plans.md) and
  [Credits and limits](./19-credits-and-limits.md).
- On the Free plan the hosted provider is visible but its models are gated —
  using one shows an upgrade prompt.

### Using a Rayu API key in the CLI (instead of a login)

This section is about signing the **CLI** in. To call Rayu models from your own
code instead, see [API keys and the Rayu API](./15-api-keys.md) — same key, but
a different base URL and request shape.

For headless or CI use you can skip the browser sign-in and paste a Rayu **API
key** (created at `rayucode.com/dashboard/api-keys`):

- First run: choose **"Use a Rayu API key"**.
- Later: `/connect` → **"Rayu — hosted models (rayucode.com API key)"**.
- Or set `RAYU_API_KEY` in your environment — Rayu imports it at startup.

The key reaches the same hosted catalog (native thinking included) with no
account session. A Rayu login and a Rayu API key are either-or credentials:
signing in with `/login` removes a previously stored key, so exactly one
Rayu credential is in use.

## Connecting a provider with `/connect`

In an interactive session:

```text
/connect
```

1. **Pick a provider** from the built-in list (the two localhost options are
   grouped under **"Localhost (Ollama / custom OpenAI-compatible endpoint)"**).
2. **Enter the credential** — usually paste an API key; some providers sign you
   in through the browser instead (Claude subscription, Vertex, Login with
   Gemini, Copilot, Kiro). Bedrock also asks for a region, Azure for the
   resource, custom/local for a base URL.
3. Rayu **fetches the provider's model catalog** and opens the model picker so
   you can choose immediately.

Rayu remembers the provider for future sessions and makes it the active one.

## Built-in providers

### Anthropic & Claude subscription

| Id | What it is | Credential |
|----|-----------|------------|
| `anthropic` | First-party Claude API (console.anthropic.com key). Native thinking and the full context window, sent directly to api.anthropic.com. | `ANTHROPIC_API_KEY` |
| `claude-subscription` | **Login with Claude** — sign in with your paid claude.ai Pro / Max plan (OAuth in the browser). Anthropic bills the subscription directly. The token is kept in secure storage. | browser sign-in |

### OpenAI-compatible endpoints

Paste the key, pick a model — everything below speaks OpenAI's
`/v1/chat/completions`, so the list is uniform:

| Id | Provider | Base URL | Env var(s) |
|----|----------|----------|------------|
| `openai` | OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| `nvidia` | NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `NVIDIA_API_KEY` |
| `deepseek` | DeepSeek | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` |
| `kimi-moonshot` | Kimi / Moonshot | `https://api.moonshot.ai/v1` | `KIMI_API_KEY`, `MOONSHOT_API_KEY` |
| `kimi-for-code` | Kimi for Code | `https://api.kimi.com/coding/v1` | `KIMI_FOR_CODE_API_KEY` |
| `glm` | GLM — Z.ai (GLM-5.2 1M ctx, native thinking) | `https://api.z.ai/api/paas/v4` | `ZAI_API_KEY`, `ZHIPUAI_API_KEY`, `GLM_API_KEY` |
| `minimax` | MiniMax (M3 1M ctx, native thinking) | `https://api.minimax.io/v1` | `MINIMAX_API_KEY` |
| `doubleword` | Doubleword | `https://api.doubleword.ai/v1` | `DOUBLE_WORD_API_KEY`, `DOUBLEWORD_API_KEY` |
| `fugu` | Fugu — Sakana AI multi-agent system | `https://api.sakana.ai/v1` | `SAKANA_API_KEY` |
| `xai` | xAI / Grok | `https://api.x.ai/v1` | `XAI_API_KEY` |
| `groq` | Groq | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` |
| `fireworks` | Fireworks AI | `https://api.fireworks.ai/inference/v1` | `FIREWORKS_API_KEY` |
| `togetherai` | Together AI | `https://api.together.xyz/v1` | `TOGETHER_API_KEY`, `TOGETHERAI_API_KEY` |
| `cerebras` | Cerebras | `https://api.cerebras.ai/v1` | `CEREBRAS_API_KEY` |
| `baseten` | Baseten | `https://inference.baseten.co/v1` | `BASETEN_API_KEY` |
| `deepinfra` | DeepInfra | `https://api.deepinfra.com/v1/openai` | `DEEPINFRA_API_KEY` |
| `huggingface` | Hugging Face Inference Providers | `https://router.huggingface.co/v1` | `HF_TOKEN`, `HUGGINGFACE_API_KEY`, `HUGGING_FACE_HUB_TOKEN` |
| `gemini` | Google Gemini API key (its OpenAI-compatible surface) | `https://generativelanguage.googleapis.com/v1beta/openai` | `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
| `ollama` | Ollama on your machine — no key needed; respects `OLLAMA_HOST` | `http://localhost:11434/v1` | — |
| `local` | Any other OpenAI-compatible server (vLLM, LM Studio, …) — you enter the base URL | *(you enter it)* | — |

### Anthropic-compatible endpoints

These providers speak Anthropic's Messages API natively, so thinking, tools and
prompt caching map 1:1:

| Id | Provider | Base URL | Env var(s) |
|----|----------|----------|------------|
| `longcat` | LongCat — Meituan (LongCat-2.0, 1M ctx) | `https://api.longcat.chat/anthropic` | `LONGCAT_API_KEY` |
| `ollama-cloud` | Ollama Cloud — ollama.com hosted models (live account model list, `:cloud` tags) | `https://ollama.com` | `OLLAMA_CLOUD_API_KEY` |

**Multiple keys, one provider:** `nvidia`, `openrouter` and `ollama-cloud` let
you store several API keys and rotate to the next one automatically when a
rate-limit error hits (paid plans).

### Google — three ways

| Id | Auth | Best for |
|----|------|----------|
| `gemini` | Gemini API key (OpenAI-compatible surface, table above) | simplicity |
| `gemini-vertex` | Google OAuth / Application Default Credentials, scoped to your GCP **project + region** | heavy use — quota lives on your project |
| `gemini-login` | Browser sign-in with a Google account (Code Assist backend, like the Gemini CLI) | free/consumer quota with zero setup |

For `gemini-vertex`, `/connect` detects ADC (e.g. from `gcloud auth
application-default login`) or runs a browser sign-in, then confirms the
project and region and fetches the catalog. The project needs the Vertex AI
API enabled, billing active, and the `roles/aiplatform.user` role — Rayu
surfaces exactly that when the API returns `403 PERMISSION_DENIED`.

### Cloud platforms

| Id | What it is | Credential |
|----|-----------|------------|
| `bedrock` | AWS Bedrock — one entry serves the whole catalog: Claude over the Anthropic Messages API, open-weight models (gpt-oss, Qwen, Kimi, …) over the OpenAI-compatible bedrock-mantle endpoint. Region-scoped (picker offers 10 common regions; default `us-east-1`); models fetched live. | `AWS_BEARER_TOKEN_BEDROCK` (Bedrock API key / bearer token) |
| `azure` | Microsoft Azure — one resource serves Claude deployments (Anthropic Messages) and Azure OpenAI deployments (Responses API). The endpoint is derived from the resource name you enter; deployments fetched live. | `ANTHROPIC_FOUNDRY_API_KEY`, `AZURE_OPENAI_API_KEY` |
| `copilot` | GitHub Copilot — uses the models in your Copilot subscription (Claude, GPT, Gemini, …). No key to paste: a GitHub device-flow sign-in exchanges for a short-lived Copilot token that auto-refreshes. | GitHub browser sign-in |
| `kiro` | Kiro — Claude models via the AWS CodeWhisperer backend. | `ksk_…` API key (`KIRO_API_KEY`) or an existing `kiro-cli` login / browser sign-in |

### Aggregators & custom

| Id | What it is | Env var(s) |
|----|-----------|------------|
| `openrouter` | OpenRouter — one key, hundreds of models; multi-key rotation supported | `OPENROUTER_API_KEY` |
| `custom` | Your own provider: give it a name, **pick the API format** its endpoint speaks (OpenAI Chat, OpenAI Responses, or Anthropic Messages), enter base URL, key and model ids, and declare thinking/image support so Rayu never sends parameters the endpoint would reject | — |

## Provider keys from the environment (headless / CI)

**Auto-import.** On startup Rayu reads the environment and a project-local
`.env` file and imports any known provider key, so providers you already have
keys for are ready without running `/connect`. The first imported provider
becomes active if none is set yet. Example `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
NVIDIA_API_KEY=nvapi-xxxxx
AWS_BEARER_TOKEN_BEDROCK=aws-xxxxx
```

The per-provider env names are in the tables above — this section is the
reference for them. For the Rayu hosted catalog, use `RAYU_API_KEY`. See
[Configuration](./05-configuration.md) for the rest of Rayu's settings.

## Switching providers and models

- `/connect` — add or reconfigure a provider, then pick its model.
- `/model` — switch models across **all** connected providers; choosing a model
  that belongs to another provider switches the active provider automatically.
- `/status` — see the active provider and model.

## Security

- API keys are stored securely on your machine. A provider's credential is only
  ever sent to that provider's configured host; keys are never logged or echoed.
- OAuth tokens (Claude subscription, Gemini, Copilot) are refreshed
  automatically and stored securely.

Next: [Models →](./04-models.md)
