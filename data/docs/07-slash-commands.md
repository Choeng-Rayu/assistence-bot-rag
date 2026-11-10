# 7. Slash Commands

Slash commands run **inside an interactive session** (terminal or the RayuCode
VS Code panel). Type `/` to open the command menu, start typing to filter,
press Enter to run.

Type `/help` in a session to list exactly what is available to you.

Arguments in `[brackets]` are optional; `<>` means required.

---

## Session & context

| Command | Description |
|---------|-------------|
| `/help` | Show help and available commands. |
| `/context` | Visualize current context usage as a colored grid. |
| `/compact [instructions]` | Clear conversation history but keep a summary in context; optional instructions steer the summarization. |
| `/clear` (aliases `reset`, `new`) | Clear conversation history and free up context. |
| `/resume [id or search term]` (alias `continue`) | Resume a previous conversation. |
| `/rename [name]` | Rename the current conversation. |
| `/tag` | Toggle a searchable tag on the current session. |
| `/branch [name]` (alias `fork`) | Create a branch of the current conversation at this point. |
| `/rewind` (alias `checkpoint`) | Restore the code and/or conversation to a previous point. |
| `/keep [file]` | Keep pending Rayu file changes. |
| `/undo [file\|all]` | Undo pending Rayu file changes (`all` undoes everything). |
| `/diff` | View uncommitted changes and per-turn diffs. |
| `/files` | List all files currently in context. |
| `/export [filename]` | Export the current conversation to a file or clipboard. |
| `/copy [N]` | Copy Rayu's last response to clipboard (or the Nth-latest). |
| `/btw <question>` | Ask a quick side question without interrupting the main conversation. |
| `/exit` (alias `quit`) | Exit the session. |

---

## Model & providers

| Command | Description |
|---------|-------------|
| `/connect` | Connect an LLM provider: pick provider, enter API key, choose a model. See [Providers](./03-providers.md). |
| `/model [model]` | Set the AI model for the session (searchable picker across connected providers). See [Models](./04-models.md). |
| `/effort [low\|medium\|high\|max\|auto]` | Set effort level for model usage. |
| `/subagent_models [AGENT] [default\|show]` (aliases `model_subagent`, `subagent_model`) | Set models for all subagents or one named agent. |
| `/webfetch_model [default\|show]` | Set the model the WebFetch tool uses. |

---

## Modes & planning

| Command | Description |
|---------|-------------|
| `/plan [open\|description]` | Enable plan mode or view the current session plan. |
| `/agent [list\|discover\|start\|adopt\|send\|attach …]` | Manage external agent CLIs (Codex, Claude Code, OpenCode): discover, start, adopt, assign work, attach. |
| `/ultraplan [task]` | Deep multi-agent planning: explore in parallel, weigh approaches, produce a step-by-step plan for approval — runs locally on your provider. |
| `/ultrareview [PR]` | Deep bug-hunt on your branch: parallel review subagents find and verify bugs — runs locally on your provider. |
| `/review` | Review a pull request. |
| `/security-review` | Security review of the pending changes on the current branch. |
| `/pr-comments` | Get comments from a GitHub pull request. |
| `/tasks` (alias `bashes`) | List and manage background tasks. |
| `/agents` | Manage agent configurations. |

---

## Billing & account

These commands need a signed-in Rayu account or a Rayu API key — see
[API keys & credentials](./15-api-keys.md).

| Command | Description |
|---------|-------------|
| `/login` | Sign in to your Rayu account. |
| `/logout` | Sign out of your Rayu account. |
| `/billing` | Show your current Rayu plan and upgrade on the web. |
| `/topup` (alias `buy-credits`) | Buy additional Rayu credits (pay-as-you-go). |
| `/usage` | Show your Rayu plan + hosted-model usage (credits & tokens). |
| `/stats` | Show your Rayu usage statistics and activity. |
| `/insights` | Generate a report analyzing your Rayu sessions. |

See [Subscription plans](./18-subscription-plans.md) and
[Credits & limits](./19-credits-and-limits.md).

---

## Remote & integration

| Command | Description |
|---------|-------------|
| `/web-bridge [pair\|status\|off]` | Connect this session to Rayu Studio's remote page with your account or a QR code. |
| `/session` (alias `remote`) | Show remote session URL and QR code (remote-mode sessions only). |
| `/ide [open]` | Manage IDE integrations and show status. |
| `/install-github-app` | Set up Rayu GitHub Actions for a repository. |

---

## Configuration & appearance

| Command | Description |
|---------|-------------|
| `/config` (alias `settings`) | Open the config panel. |
| `/permissions` (alias `allowed-tools`) | Manage allow & deny tool permission rules. |
| `/sandbox` | Toggle or configure bash sandboxing (`exclude "pattern"` to edit the exclusion list). |
| `/theme` | Change the terminal theme. |
| `/color <color\|default>` | Set the prompt bar color for this session. |
| `/brandmark` | Customize Rayu's brand mark glyph and loading-spinner style. |
| `/banner` | Toggle the startup mascot banner on or off. |
| `/mascot` | Select which mascot the startup banner shows. |
| `/vim` | Toggle between Vim and Normal editing modes. |
| `/keybindings` | Open or create your keybindings configuration file. |
| `/statusline` | Set up Rayu's status line UI. |
| `/terminal-setup` | Install Shift+Enter / Option+Enter key binding for newlines (hidden when your terminal supports it natively). |
| `/output-style` | Deprecated: use `/config` to change output style. |

---

## Memory & project

| Command | Description |
|---------|-------------|
| `/init` | Initialize a new RAYU.md file with codebase documentation. |
| `/memory` | Edit Rayu memory files. |
| `/add-dir <path>` | Add a new working directory. |
| `/review_detail [file]` | Show detailed pending Rayu file change diffs. |
| `/hooks` | View hook configurations for tool events. |

---

## Skills & plugins

| Command | Description |
|---------|-------------|
| `/skills` | List available skills. |
| `/install-skill <owner/repo \| url \| path> [--overwrite]` | Install a skill from a GitHub repo, a SKILL.md URL, or a local path. |
| `/plugin` (aliases `plugins`, `marketplace`) | Manage Rayu plugins. |
| `/reload-plugins` | Activate pending plugin changes in the current session. |

---

## Status & feedback

| Command | Description |
|---------|-------------|
| `/doctor` | Diagnose and verify your Rayu installation and settings. |
| `/status` | Show version, model, account, API connectivity, and tool statuses. |
| `/feedback [report]` (alias `bug`) | Send feedback about RayuCode (bug, idea, or other). |
| `/contact_me` | Contact the developer. |

Next: [CLI Reference →](./06-cli-reference.md)
