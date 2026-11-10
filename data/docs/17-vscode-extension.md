# VS Code Extension (RayuCode)

RayuCode is the Rayu AI coding agent inside Visual Studio Code. It is **not a
separate product with fewer features** — it is the second face of the same
tool you use in the terminal.

## One engine, two surfaces

The Rayu CLI and the RayuCode extension run the same Rayu agent. When you open
a RayuCode session, the extension runs that agent in the background for your
editor, with the same capabilities as the terminal.

That means everything you can do in the terminal works in the editor too:

- every built-in tool (file read/write/edit, bash, web search, LSP, …)
- every [slash command](./07-slash-commands.md) (`/model`, `/connect`,
  `/web-bridge`, billing commands, …)
- every [provider](./03-providers.md) — Rayu-hosted models or your own keys
- skills and agent configurations

The extension is the UI: the chat lives in your editor tabs, and a sidebar
panel manages sessions and providers. Anything the agent does, both surfaces
get it.

## Install

Requirements: a current version of VS Code and a workspace folder you have
trusted (see [Limitations](#limitations)).

The extension is published on the VS Code Marketplace as
**`RayuCode.rayucode`**. Any of these works:

| Route | How |
|---|---|
| One-click | [rayucode.com/download](https://rayucode.com/download) → "Install" on the VS Code Extension card. Uses the `vscode:extension/RayuCode.rayucode` protocol link, which opens your local VS Code with the install prompt ready. |
| Marketplace search | Open the Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`), search **RayuCode**, publisher `RayuCode`. |
| Command line | `code --install-extension RayuCode.rayucode` |

After install, a green **RayuCode** icon appears in the Activity Bar (the
vertical icon strip on the side).

## First session

1. Click the RayuCode icon in the Activity Bar.
2. Sign in (see below) — or pick a model first and use a provider key.
3. Click **New Session** (the `+` in the panel header, or the
   `RayuCode: New Session` command).
4. Type your task and press Enter. The conversation opens as an **editor tab**,
   next to your code files.

## Signing in

Two things worth knowing up front:

- **The extension uses the same Rayu account and provider setup as the CLI.**
  Signing in from the editor gives you the same models and credentials, and a
  key connected in one surface is available in the other.
- Running a turn requires *either* a signed-in Rayu account *or* a connected
  provider key.

### Path 1 — Rayu account (hosted models)

Use the panel's sign-in prompt or the `RayuCode: Sign In` command. Your browser
opens the Rayu sign-in page; approve there and the editor picks up the
credential automatically. If the browser does not open, the extension offers a
**Copy sign-in link** button so you can paste the URL manually. The wait is
cancelable and gives up with a clear message after a few minutes.

With a Rayu account you get hosted models billed in credits — see
[Subscription plans](./18-subscription-plans.md). Use `RayuCode: Sign Out` (or
the panel) to forget the credential.

### Path 2 — bring your own API key

Run `/connect` in the session composer (or open **Provider setup** in the
sidebar) and follow the picker — the same flow as the CLI. Choose a provider,
paste your key, and the session runs against that provider directly. Keys are
stored in your provider setup, not in the chat history.

### Remote-SSH note

Account sign-in needs a browser on your machine to complete a callback on the
session's machine. Over **Remote-SSH** that round-trip can fail — the login
page may never complete, and you will see a sign-in timeout. The reliable path
on remote workspaces is **API-key setup with `/connect`** in the remote
terminal. See [Troubleshooting](./10-troubleshooting.md) for details.

## Panel tour

The extension is organized around two ideas: the **conversation goes in an
editor tab**, and the **sidebar is the management hub** — it never shows a
second copy of the chat.

### Sidebar (Activity Bar → RayuCode)

The sidebar panel, "Sessions", is the control hub:

- **Session list** — start, switch between, and retire conversations. Each one
  opens as its own editor tab; several can run side by side, and switching tabs
  never interrupts a turn in flight.
- **Background tasks** — long-running tool work and delegated agents with their
  progress.
- **Provider setup** — connect providers and API keys (`/connect` flow).
- **Sign-in state** — who you are signed in as, with sign-in / sign-out.

### Sessions as editor tabs

Each conversation is a normal editor tab: open files in one pane, the agent in
another, arrange them however you like. The composer supports:

- **Slash-command palette** — type `/` to get the command list, the same
  commands the CLI has.
- **`@` file mentions** — type `@` to reference workspace files; the engine
  expands them into context, including directories.

### Permission modes

A pill in the composer header shows the current mode. Press **Shift+Tab** to
cycle through them (least to most permissive, then back to the start):

| Mode | What it allows |
|---|---|
| **Ask** (default) | Asks before running any tool that changes something. |
| **Auto-edit** | Applies file edits without asking; still asks before running commands. |
| **Plan** | Read and analyse only — no edits, no commands. The agent proposes a plan for your approval. |
| **Full Manage** | Runs all non-interactive tools without asking. |

### Review cards (keep / undo)

When the agent changes files, a review card appears in the transcript listing
the changed files. Open any file to see a **side-by-side diff** — the "before"
side is the exact snapshot Rayu recorded before editing (not git HEAD), so your
own uncommitted changes never show up as if Rayu made them.

- **Keep** / **Undo** work **per file** or in bulk. They run the agent's own
  `/keep` and `/undo` commands, including the protection that refuses to undo a
  file you have since edited by hand.
- Each session tab keeps its own review state, so two conversations editing the
  same file diff independently.

### Adding context from anywhere in the editor

| Action | Where |
|---|---|
| **Add to Rayu Context** | Right-click a file or folder in the Explorer, a selection in an editor, or an editor tab's title menu. Inserts an `@`-mention into the composer. |
| **Add Terminal Selection to Prompt** | Right-click a selection in the integrated terminal. |
| Drag and drop | Drop a file onto the session panel to attach it. |

The live context-window gauge in the panel header shows how full the
conversation is, so you know when to compact or start a new session.

## Remote features from the extension

- **Web Bridge** — run `/web-bridge` in a session (or use the pairing entry in
  the panel) to let Rayu Studio attach to the live session from a browser tab:
  streamed deltas, tool approvals, plan approvals, prompts from your phone or
  another machine.

## Extension commands

Beyond in-session slash commands, the extension contributes these VS Code
commands (Command Palette, prefix `RayuCode:`):

| Command | Does |
|---|---|
| `New Session` | Start another conversation (also the `+` in the panel header). |
| `Sign In` / `Sign Out` | Manage the Rayu account credential for the editor. |
| `Add to Rayu Context` | Explorer / editor / tab context menu: insert an `@`-mention. |
| `Add Terminal Selection to Prompt` | Terminal context menu: copy the selection into the composer. |
| `Send Feedback` | Report an issue or share feedback. |

## Limitations

- **Workspace trust is required.** The agent executes commands, edits files,
  and reads the workspace's `.env` and plugins, so it is disabled in Restricted
  Mode. If RayuCode looks dead in a folder, VS Code is asking you to **trust the
  workspace** first — click "Trust" on the prompt, or run
  *Workspaces: Trust Workspace*.
- **There is no reduced-capability mode** for an untrusted folder; trust the
  workspace or use the terminal.
- **Remote-SSH account sign-in may fail** as described above; use `/connect`
  with an API key there.

## Troubleshooting

Quick pointers:

| Symptom | Try |
|---|---|
| Panel says "trust required" / no sessions start | Trust the folder (see Limitations). |
| Sign-in spins, then times out | Sign in within a few minutes; on Remote-SSH use `/connect` instead. If the browser never opens, use the "Copy sign-in link" button. |
| Hosted requests return 401 / "please sign in" | Re-run Sign In, or check your plan — hosted models need a Rayu account ([plans](./18-subscription-plans.md)). |

More on the [Troubleshooting](./10-troubleshooting.md) page.

## See also

- [Quickstart](./02-quickstart.md) — the same first session in the terminal
- [Subscription plans & what they include](./18-subscription-plans.md) — what
  your account covers in either surface
- [Providers](./03-providers.md) — hosted vs bring-your-own-key
- [Slash Commands](./07-slash-commands.md) — everything the agent understands
  in the composer
