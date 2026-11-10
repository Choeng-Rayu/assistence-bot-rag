# 5. Configuration

Rayu is configured from three places, roughly in order of "how you touch them":

1. **`/config`** — the in-session settings panel (easiest).
2. **Settings files** — JSON files that merge in a fixed hierarchy (below).
3. **Memory files** — `RAYU.md` / `AGENTS.md` instructions the model reads.

## Where Rayu stores your settings

All user state lives in **`~/.rayu`**:

| Path | Purpose |
|------|---------|
| `settings.json` | Your user settings — see below |
| `config.json` | App state Rayu manages for you (UI preferences, MCP server toggles, subagent model selections) — normally edited only via commands like `/mcp` and `/subagent_models` |
| `plans/` | Session plan files (`plansDirectory` to relocate) |
| `projects/` | Per-project session transcripts — retention: `cleanupPeriodDays` (default 30) |
| `skills/`, `agents/` | User skills and agent definitions |

## Settings file hierarchy

Settings are JSON files merged in this order — **later sources override
earlier ones per key** (permission rule and allowlist arrays merge instead of
replacing):

| # | File | Scope | Notes |
|---|------|-------|-------|
| 1 | `~/.rayu/settings.json` | User (all projects) | created by `/config` |
| 2 | `.rayu/settings.json` | Project (checked in) | team-shared; applies once you trust the folder |
| 3 | `.rayu/settings.local.json` | Project-local (personal) | your overrides for this repo; add to `.gitignore` |

Two escape hatches for the hierarchy: `rayu --settings <file-or-json>` layers
extra settings onto one run, and `rayu --setting-sources user,project,local`
restricts which files load at all.

## Key settings in `settings.json`

Every key is optional; unknown or invalid keys are ignored (and kept in the
file so you can fix them). Commonly used keys:

| Key | Type | Meaning |
|-----|------|---------|
| `model` | string | Default model for sessions. |
| `availableModels` | string[] | Allowlist of selectable models. |
| `permissions.allow` / `.deny` / `.ask` | rule[] | Tool permission rules, e.g. `"Bash(git:*)"`, `"Edit(~/.rayu/**)"`. |
| `permissions.defaultMode` | enum | Starting permission mode: `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`, `fullManage`, `orchestrator`. |
| `permissions.additionalDirectories` | string[] | Extra directories inside permission scope. |
| `hooks` | object | Commands/scripts to run before or after tool events (`/hooks` to inspect). |
| `env` | object | Environment variables to set inside Rayu sessions. |
| `statusLine` | object | Custom status line: `{ "type": "command", "command": "..." }` (`/statusline`). |
| `outputStyle` | string | Output style for responses (`/config` preferred). |
| `language` | string | Preferred response language, e.g. `"spanish"`. |
| `sandbox` | object | Bash sandboxing policy (`/sandbox`). |
| `worktree.symlinkDirectories` / `.sparsePaths` | string[] | Symlink big dirs (e.g. `node_modules`) into worktrees; sparse-checkout monorepos (`-w`). |
| `otelHeadersHelper` | string | Script that outputs OpenTelemetry headers. |
| `enabledPlugins` | object | Enabled plugins, keyed `plugin@marketplace`. |
| `apiKeyHelper` | string | Script that outputs an auth value. |
| `attribution` | object | Custom commit/PR attribution text. |
| `cleanupPeriodDays` | number | Transcript retention (default 30; `0` disables persistence). |
| `plansDirectory` | string | Where plan files are saved (default `~/.rayu/plans/`). |
| `effortLevel` | enum | Persisted effort: `low`, `medium`, `high`. |
| `alwaysThinkingEnabled` | boolean | Master switch for model thinking. |
| `agent` | string | Run the main thread as a named agent. |
| `autoMemoryEnabled` / `autoMemoryDirectory` | bool / string | Cross-session auto memory. |
| `claudeMdExcludes` | string[] | Glob/path patterns of memory files to skip loading. |
| `brandGlyph` / `spinnerStyle` | string | Brand mark glyph and spinner animation (`/brandmark`). |
| `respectGitignore` | boolean | Whether the `@` file picker honors `.gitignore` (default true). |

Example:

```json
{
  "model": "deepseek-v4-flash",
  "permissions": {
    "allow": ["Bash(git:*)", "Read(./docs/**)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"],
    "defaultMode": "acceptEdits"
  },
  "hooks": {},
  "cleanupPeriodDays": 90
}
```

## Memory files: `RAYU.md` & `AGENTS.md`

Memory files are standing instructions the model reads at startup. Rayu
collects them in this order (later = higher priority):

| Tier | Location | Use |
|------|----------|-----|
| User | `~/.rayu/RAYU.md` | Your private instructions across all projects |
| Project | `RAYU.md`, `AGENTS.md`, `CLAUDE.md`, `.rayu/RAYU.md`, `.rayu/rules/*.md` — searched from the current directory up to the root | Checked-in team conventions |
| Local | `RAYU.local.md` | Your private per-project notes (keep it out of git) |

- When project `RAYU.md` and `AGENTS.md` conflict, `RAYU.md` takes precedence.
- Any memory file can pull in others with `@path` includes
  (`@./file`, `@~/file`, `@/abs/path`).
- `/init` generates a starter project `RAYU.md`; `/memory` opens the memory
  files for editing; `claudeMdExcludes` in settings skips specific files.
- `--bare` disables memory-file discovery entirely.

Next: [CLI Reference →](./06-cli-reference.md)
