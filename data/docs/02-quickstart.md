# 2. Quickstart

The fastest path is your Rayu account: sign in once and Rayu's hosted models
are ready to use — no API keys, no provider setup. Bring-your-own-key (BYOK)
works too and is fully covered in [Providers](./03-providers.md).

## 1. Install and start

```bash
rayu
```

(Not installed yet? See [Installation](./01-installation.md).)

On the very first launch Rayu asks you to pick a theme, then shows a short
setup screen.

## 2. Connect Rayu

The setup screen offers two ways to get a credential:

1. **Sign in to Rayu — opens your browser (recommended)**
2. **Use a Rayu API key — paste a key created at `rayucode.com/dashboard/api-keys`**

Choose the first one. Rayu opens your browser to sign in, you approve, and the
terminal finishes on its own.

You'll see:

```text
Signed in to Rayu as you@example.com.
```

What just happened:

- Your session is stored securely on your machine and refreshes automatically;
  sign out any time with `/logout`.
- If the browser doesn't open (SSH, WSL, headless machine), the sign-in link is
  printed in the terminal — copy it into any browser.
- With a paid plan, the **Rayu hosted provider is activated automatically** —
  no `/connect`, no API key. See [Subscription plans](./18-subscription-plans.md).

You can also run `/login` later at any time to switch accounts.

> On this first screen you need a Rayu credential (account or API key). Other
> providers — Anthropic, OpenAI, DeepSeek, local models, … — are added right
> after it with `/connect`, and are fully documented in
> [Providers](./03-providers.md).

## 3. Trust the folder

Rayu can read, edit, and run files in your current directory, so the first time
you open it in a folder it asks you to confirm you trust it. Choose yes to
continue. (Permission prompts for individual actions still apply — see
[CLI Reference](./06-cli-reference.md).)

## 4. Pick a model

```text
/model
```

Open the picker and choose a hosted model — e.g. **DeepSeek V4 Pro** or any
model your plan includes. You'll see the choice in the status line, like:

```text
deepseek-v4-pro · Rayu
```

The hosted catalog is live and updated regularly, so what you see is what is
available today — see [Models](./04-models.md).

## 5. Ask for your first task

```text
> explain what this project does and list its main modules
```

Rayu streams its answer, reads files, and proposes edits or commands with a
confirmation prompt each time. Press `Esc` to cancel a running turn; `Ctrl+C`
twice to exit.

Useful while you go (type `/` to see all commands):

| Command | Action |
|---------|--------|
| `/model` | Search & switch models across all connected providers |
| `/connect` | Add or switch to another provider (BYOK) |
| `/usage` | Your credits and plan usage |
| `/billing` | Plan, balance and invoices |
| `/context` | Context-window usage for the current session |
| `/clear` | Start a fresh conversation |
| `/exit` | Quit |

## Headless / one-shot use

Run a single prompt and print the result without the interactive UI:

```bash
rayu -p "write a one-line summary of package.json"
```

Sign in once and scripts use your hosted models automatically — no keys in the
environment. JSON output for pipelines:

```bash
rayu -p --output-format json "list top-level modules" | jq .result
```

More flags (`--model`, `--permission-mode`, subagents, session options) are in
the [CLI Reference](./06-cli-reference.md).

## In VS Code instead?

**RayuCode** is the same agent inside VS Code — same account, same models.
Install it from the Marketplace or <https://rayucode.com/download>; see
[VS Code Extension](./17-vscode-extension.md).

## Bring your own key instead

Already hold an Anthropic, OpenAI, NVIDIA, DeepSeek (or any other) API key?

```text
/connect
```

Pick the provider, paste your key, choose a model — that's it. Keys are stored
securely on your machine, requests go **directly to the provider**, and you keep
full control of billing. The full provider list, environment auto-import, and
headless setup are documented in [Providers](./03-providers.md).

One note: BYOK models use your own provider billing; Rayu plans and credits
cover the hosted catalog — see [Credits and limits](./19-credits-and-limits.md).

Next: [Providers →](./03-providers.md)
