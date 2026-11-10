# 6. CLI Reference

```text
rayu [options] [prompt]
rayu <subcommand> [options]
```

- No subcommand and no `--print` → **interactive** session (terminal UI).
- `-p` / `--print` (or piped stdin) → **non-interactive** one-shot run.
- A subcommand (`mcp`, `plugin`, `doctor`, …) runs that subcommand.

---

## Model, effort & tools

| Flag | Description |
|------|-------------|
| `--model <model>` | Model for this session: an alias or a full id (provider-dependent, e.g. `deepseek-chat`). See [Models](./04-models.md). |
| `--effort <level>` | Effort level: `low`, `medium`, `high`, `max`. |
| `--fallback-model <model>` | Automatically fall back to this model when the default is overloaded (`--print` only). |
| `--betas <betas...>` | Beta API headers to include (API-key providers only). |
| `--agent <agent>` | Run as a named agent (built-in or custom); overrides the `agent` setting. |
| `--agents <json>` | Define custom agents inline, e.g. `'{"reviewer": {"description": "Reviews code", "prompt": "You are a code reviewer"}}'`. |
| `--tools <tools...>` | Restrict the built-in tool set: `""` disables all, `"default"` uses all, or name them (`"Bash,Edit,Read"`). |
| `--allowed-tools <tools...>` | Tools allowed without prompting, e.g. `"Bash(git:*) Edit"`. Also `--allowedTools`. |
| `--disallowed-tools <tools...>` | Tools denied outright. Also `--disallowedTools`. |

## Sessions & history

| Flag | Description |
|------|-------------|
| `-c, --continue` | Continue the most recent conversation in the current directory. |
| `-r, --resume [id\|term]` | Resume a session by ID, or open the interactive picker (optional search term). |
| `--from-pr [pr\|term]` | Resume the session linked to a PR (number or URL), or open the picker. |
| `--fork-session` | When resuming, create a new session id instead of reusing the original. |
| `--session-id <uuid>` | Use a specific session UUID (must not already exist). |
| `-n, --name <name>` | Display name for the session (shown in `/resume` and the terminal title). |
| `--no-session-persistence` | Do not save the session to disk (`--print` only). |

## Permissions & safety

| Flag | Description |
|------|-------------|
| `--permission-mode <mode>` | Session permission mode — see the table below. |
| `--dangerously-skip-permissions` | Bypass all permission checks. Only for sandboxes with no internet access. |
| `--allow-dangerously-skip-permissions` | Make the bypass option available without activating it by default. |

Bash sandboxing is configured in `settings.json` (see
[Configuration](./05-configuration.md)), not via a CLI flag.

| Mode | Behavior |
|------|----------|
| `default` | Ask before any tool that modifies files or runs commands. |
| `acceptEdits` | Auto-accept file edits; still ask before shell commands. |
| `plan` | Research and plan only — no execution. |
| `dontAsk` | Run tools without prompting. |
| `bypassPermissions` | Run everything without prompting (sandbox/CI only). |
| `fullManage` | Full tool-management mode. |
| `orchestrator` | Start in delegation mode. |

## Context & directories

| Flag | Description |
|------|-------------|
| `--add-dir <dirs...>` | Allow tool access to additional directories (space-separated). |
| `--system-prompt <prompt>` | Replace the default system prompt for this session. |
| `--append-system-prompt <prompt>` | Append text to the default system prompt. |
| `--settings <file-or-json>` | Load extra settings from a JSON file path or inline JSON string. |
| `--setting-sources <sources>` | Comma-separated sources to load: `user`, `project`, `local`. |
| `--file <specs...>` | Download file resources at startup (`file_id:relative_path`). |

## MCP & plugins

| Flag | Description |
|------|-------------|
| `--mcp-config <configs...>` | Load MCP servers from JSON files or inline JSON (space-separated). |
| `--strict-mcp-config` | Use only MCP servers from `--mcp-config`; ignore every other MCP config. |
| `--plugin-dir <path>` | Load plugins from a directory for this session only. Repeatable: `--plugin-dir A --plugin-dir B`. |
| `--disable-slash-commands` | Disable all skills/slash commands for this session. |

## Worktree, IDE & browser

| Flag | Description |
|------|-------------|
| `-w, --worktree [name]` | Run this session in a fresh git worktree (optionally named). |
| `--tmux` | Create a tmux session for the worktree (requires `--worktree`; `--tmux=classic` for traditional tmux). |
| `--ide` | Auto-connect to the IDE on startup when exactly one valid IDE is available. |
| `--chrome` / `--no-chrome` | Enable / disable Rayu-in-Chrome integration. |

## Output & diagnostics

| Flag | Description |
|------|-------------|
| `-p, --print` | Print the response and exit (non-interactive). Trust dialog is skipped — run only in trusted directories. |
| `--output-format <fmt>` | With `--print`: `text` (default), `json`, `stream-json`. |
| `--input-format <fmt>` | With `--print`: `text` (default) or `stream-json`. |
| `--json-schema <schema>` | Validate/constrain the final output against a JSON Schema (`--print` only). |
| `--include-partial-messages` | Emit partial message chunks as they arrive (`--print` + `stream-json`). |
| `--include-hook-events` | Include hook lifecycle events in the output stream (`stream-json`). |
| `--replay-user-messages` | Re-emit stdin user messages on stdout for acknowledgment (both stream formats). |
| `--max-turns <n>` | Stop after N agentic turns (`--print` only). |
| `--max-budget-usd <amount>` | Cap API spend for the run (`--print` only). |
| `--task-budget <tokens>` | API-side task budget in tokens (`--print` only). |
| `-d, --debug [filter]` | Debug logging with optional category filter (`"api,hooks"`, `"!1p,!file"`). |
| `--debug-file <path>` | Write debug logs to a file (implicitly enables debug). |
| `--verbose` | Override the verbose-mode setting. |
| `--bare` | Minimal mode: skip hooks, LSP, plugin sync, auto-memory, keychain reads, and RAYU.md discovery. Supply context explicitly (`--system-prompt`, `--add-dir`, `--mcp-config`, `--settings`, `--agents`, `--plugin-dir`). |
| `-v, --version` | Print version. |
| `-h, --help` | Show help. |

> **Provider note:** `--model` accepts any model your active provider serves.
> To choose the *provider* itself, use `/connect` inside a session or set a
> provider key environment variable (see
> [Providers](./03-providers.md), "Provider keys from the environment"). See
> also [Configuration](./05-configuration.md).

---

## Headless usage (`-p`)

`--print` makes Rayu pipe-friendly: give it a prompt (or stdin), it answers,
it exits.

```bash
# Plain text — good in scripts
rayu -p "explain what src/auth.ts does"

# Pipe in context
cat error.log | rayu -p "summarize the failure and suggest a fix"

# Machine-readable result
rayu -p --output-format json "list the modules" | jq -r '.result'
```

`--output-format json` returns one object with `result`, `usage`,
`total_cost_usd`, `num_turns`, and `session_id`.
`--output-format stream-json` returns newline-delimited JSON events in real
time — pair it with `--input-format stream-json` to drive a long-running
session over stdin:

```bash
echo '{"type":"user","message":{"role":"user","content":"hello"}}' \
  | rayu -p --input-format stream-json --output-format stream-json
```

Structured output validated against a schema:

```bash
rayu -p --output-format json \
  --json-schema '{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}' \
  "Give me the package name of this repo"
```

CI-friendly limits and session control:

```bash
rayu -p --max-turns 10 --max-budget-usd 0.50 --output-format json "fix the lint errors"
rayu -p --session-id 123e4567-e89b-42d3-a456-426614174000 "review this diff"   # fixed id
rayu -p --no-session-persistence "one-off question"                             # nothing saved
rayu -c -p "continue: now add tests"                                            # resume last session
```

---

## Subcommands

| Command | Description |
|---------|-------------|
| `rayu mcp …` | Manage MCP servers (see below). |
| `rayu plugin …` (alias `plugins`) | Manage plugins and marketplaces (see below). |
| `rayu agents` | List configured agents. |
| `rayu doctor` | Check installation and settings health. |
| `rayu update` / `rayu upgrade` | Check for updates and install if available. |
| `rayu install [target]` | Install a Rayu release (`stable`, `latest`, or a version; `--force` to reinstall). |
| `rayu uninstall` / `rayu remove` | Uninstall the Rayu CLI. |
| `rayu completion <bash\|zsh\|fish>` | Print (or `--output <file>` write) a shell completion script. |

### `rayu mcp`

| Command | Description |
|---------|-------------|
| `rayu mcp add <name> <command\|url> [args...]` | Add a server. `-t stdio\|sse\|http` picks the transport (default stdio), `-s local\|user\|project` the scope, `-e KEY=val` env vars, `-H "Header: val"` headers, `--client-id` / `--client-secret` / `--callback-port` for OAuth. |
| `rayu mcp add-json <name> <json>` | Add a server from a JSON string. `-s <scope>` (default `local`). |
| `rayu mcp list` | List configured servers (health-checks stdio servers — run in trusted dirs). |
| `rayu mcp get <name>` | Show one server's details. |
| `rayu mcp remove <name>` | Remove a server (`-s <scope>` optional — auto-detects). |
| `rayu mcp serve` | Start Rayu itself as an MCP server. |
| `rayu mcp reset-project-choices` | Forget all approved/rejected `.mcp.json` servers for this project. |

### `rayu plugin`

| Command | Description |
|---------|-------------|
| `rayu plugin validate <path>` | Validate a plugin or marketplace manifest. |
| `rayu plugin list` | List installed plugins (`--json`; `--available` adds marketplace listings). |
| `rayu plugin install <plugin>` | Install from a marketplace (`plugin@marketplace` to choose one; `-s user\|project\|local`). |
| `rayu plugin uninstall <plugin>` | Uninstall (aliases `remove`, `rm`; `--keep-data` preserves plugin data). |
| `rayu plugin enable <plugin>` / `rayu plugin disable [plugin]` | Toggle plugins (`disable -a` disables all). |
| `rayu plugin update <plugin>` | Update to the latest version (restart to apply). |
| `rayu plugin marketplace add <source>` | Add a marketplace from URL, path, or GitHub repo. |
| `rayu plugin marketplace list` / `remove <name>` / `update [name]` | Manage configured marketplaces. |

---

## Exit codes

- `0` — success.
- `1` — error (API failure, invalid arguments, or no input for `--print`).

Next: [Slash Commands →](./07-slash-commands.md)
