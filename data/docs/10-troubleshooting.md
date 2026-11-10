# 10. Troubleshooting

First stop for any runtime problem: run `/doctor` (or `rayu doctor` from the
shell). It checks your installation, settings, and connectivity and reports
what it finds.

## Installation problems

### `rayu: command not found` right after installing

The `PATH` change the installer made only applies to **new** shells. Open a new
terminal, or apply it to the current one:

```bash
export PATH="$HOME/.rayu/bin:$PATH"
```

On Windows, reopen PowerShell (the user `PATH` is read at process start).

### The installer says another `rayu` is earlier on my PATH

An older `npm install -g` copy is shadowing the new install, so `rayu` keeps
launching the old one. Remove it:

```bash
npm uninstall -g @rayu-dev/rayu-cli
which -a rayu        # confirm only ~/.rayu/bin/rayu remains
```

### `npm install -g` fails (EACCES, node-gyp, sharp, prebuild)

Use the installer instead — it needs no npm, no global prefix write access and
compiles nothing:

```bash
curl -fsSL https://rayucode.com/install | bash
```

If you must use npm, point it at a prefix you own rather than using `sudo`:

```bash
npm config set prefix ~/.npm-global
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g @rayu-dev/rayu-cli
```

### `checksum mismatch`

The download was corrupted or tampered with, and **nothing was installed**.
Retry; if it keeps happening on the same file, report it with the printed
expected/actual hashes.

### Alpine / musl, or no prebuilt runtime for my platform

The installer detects musl and uses a musl Node build. If none exists for your
architecture, install Node yourself and re-run:

```bash
apk add nodejs        # Alpine
curl -fsSL https://rayucode.com/install | bash
```

### Start over

```bash
curl -fsSL https://rayucode.com/install | bash -s -- --uninstall
rm -rf ~/.rayu        # also drops settings and credentials
curl -fsSL https://rayucode.com/install | bash
```

## API & provider errors

### API Error: 404

**Cause:** the selected model isn't a chat model on that endpoint, or the model
id is wrong. Specialized models (code completion, embedding, vision-only
variants) can return 404 on a chat endpoint.

**Fix:** switch to an instruction/chat model with `/model` (e.g.
`meta/llama-3.3-70b-instruct`, `deepseek-chat`). You can also start with a
known-good model for one run:

```bash
rayu --model meta/llama-3.3-70b-instruct
```

### API Error: 401 / 403 (bring-your-own-key provider)

**Cause:** missing, invalid, or expired API key for the active provider — or a
model the provider does not grant your key access to.

**Fix:** re-enter the key with `/connect`, then pick the model again with
`/model`. `/status` shows which provider is active, so check it when a key you
set doesn't seem to be reaching the endpoint.

### 401 on Rayu-hosted models

**Cause:** your Rayu sign-in is stale or expired, or your plan no longer
includes the model.

**Fix:** run `/login` and complete the browser sign-in again. If you use a Rayu
API key instead of an account sign-in, verify or regenerate that key on the
dashboard's API-keys page.

### "Not logged in · Run /login"

**Cause:** nothing is configured for the active path — no Rayu account sign-in
and no provider key.

**Fix:** run `/login` (Rayu account, hosted models on a plan), or `/connect`
to enter a provider API key. `/status` shows which provider and key source are
actually active.

### API Error: 429

**Cause:** provider rate limit / quota. Not a Rayu bug — the request reached the
provider.

**Fix:** wait and retry, slow down requests, or switch provider/model. On
hosted plans a 429 means a plan pacing window (weekly / 5-hour) is full —
see [Credits & Limits](./19-credits-and-limits.md).

### "API Error: Connection error."

**Cause:** the provider endpoint is unreachable — wrong base URL, no network,
DNS failure, or a local server that isn't running.

**Fix:** check your network, then review the provider's base URL under
**Provider setup** (or re-run `/connect`). For a local OpenAI-compatible server,
confirm it is running and that the URL ends with the right path (usually `/v1`).

## Model behaviour

### Wrong context window

**Cause:** the number shown comes from the model's advertised context window,
and some entries report a different limit than the model actually supports.

**Fix:** choose the matching model entry with `/model`; if the gauge is already
near the limit, run `/compact` or start a new session so the conversation stays
inside the real window.

### `/model` or `/connect` doesn't open

**Cause:** when typing a slash command, sending the whole string at once can be
treated as pasted text.

**Fix:** type the command normally (key by key) and press Enter. Ensure you're at
the prompt (past the trust dialog) first.

### The model over-calls tools / loops on simple prompts

**Cause:** weaker non-Claude models receive the full tool suite + system prompt
and may call tools eagerly. In non-interactive `--print` mode without
`--permission-mode bypassPermissions`, denied tools can cause retries.

**Fix:** for `--print` tool use, add `--permission-mode bypassPermissions` (sandbox
only). Interactively, you'll get permission prompts you can decline. Prefer
stronger instruct models for agentic tasks.

### A reasoning model replies with empty/blank output

**Cause:** reasoning models (`deepseek-reasoner`, Qwen/`gpt-oss`, o-series) spend
output tokens on hidden reasoning first. With a small `max_tokens` they can hit
the limit before producing the visible answer (`finish_reason: length`).

**Fix:** allow more output budget (the on-screen thinking confirms it's working).
OpenAI `o1`/`o3`/`o4`/`gpt-5` token/temperature params are handled automatically.

### Images aren't recognized

**Cause:** the selected model isn't a vision model — only vision models can read
images (pasted or returned by tools).

**Fix:** switch to a vision model with `/model`, e.g.
`meta/llama-3.2-11b-vision-instruct` (NVIDIA) or
`Qwen/Qwen3-VL-30B-A3B-Instruct-FP8` (Doubleword).

## VS Code extension (RayuCode)

### The panel stays empty / tells me to trust the workspace

**Cause:** the extension runs commands and edits files, so VS Code's workspace
trust is a hard gate; the panel stays disabled in Restricted Mode.

**Fix:** click **Trust Workspace** on the prompt (or run
*Workspaces: Trust Workspace* from the Command Palette). The panel loads once
the folder is trusted.

### Sign-in never completes (the browser opens but nothing happens)

**Cause:** the browser sign-in callback can't reach the machine running the
extension. This commonly happens when VS Code runs remotely (Remote-SSH, WSL,
containers).

**Fix:**
- Remote-SSH: account sign-in is **not supported** there. In the remote terminal
  run `/connect` and configure an API key instead.
- WSL/containers on your own machine: confirm the forwarded port under *Ports*
  in the panel. If the page still never completes, switch to `/connect` with an
  API key.

### The editor reloads or the panel dies during long sessions

**Cause:** a very large conversation can exhaust the memory the background
engine is allowed to use.

**Fix:** run `/compact` or start a new session to shrink the context. The
extension restarts the engine automatically after an unexpected stop, so a
reload usually recovers the session.

---

Still stuck? Run `/doctor` and report the on-screen error, the command you ran,
and what you expected to happen: `/feedback` sends it to the team.
