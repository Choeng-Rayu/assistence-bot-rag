# 1. Installation

Rayu ships as one product with two surfaces: the **terminal CLI** (`rayu`) and
the **RayuCode VS Code extension**. Start with the CLI below; extension
installation is covered in [VS Code Extension](./17-vscode-extension.md).

## One command, any machine

**macOS / Linux**

```bash
curl -fsSL https://rayucode.com/install | bash
```

**Windows (PowerShell)**

```powershell
irm https://rayucode.com/install.ps1 | iex
```

Run this in **Windows PowerShell 5.1 or PowerShell 7** on Windows 10/11.
A regular PowerShell window is enough; administrator access is not required.
The installer adds Rayu to the current window's `PATH`, so you can immediately
check it with `rayu --version`. Reopen any other terminals to pick up the change.

Then open a new terminal and run:

```bash
rayu
```

No `sudo` is needed, and no Node or npm install is required when a standalone
binary is published for your platform. Read the script before running it if you
prefer: <https://rayucode.com/install.sh> (<https://rayucode.com/install.ps1>
for Windows).

## What the installer does

1. Detects your OS, CPU architecture and libc (glibc vs musl).
2. Installs a **standalone binary** for your platform when one is published for
   this release — it embeds its own runtime, so nothing else is needed.
3. Otherwise installs the published JavaScript release using a Node runtime
   already on your machine (Node 18 or newer on macOS/Linux, Node 22 or newer on
   Windows). Nothing is compiled.
4. Installs the launcher into `~/.rayu/bin` — never a system directory — and adds
   that directory to your `PATH` (`.bashrc`, `.zshrc`, `.profile`,
   `config.fish`, or the Windows user `PATH`).
5. Verifies the result by running `rayu --version` before reporting success.

Every download is checksum-verified. A mismatch aborts the install and changes
nothing.

## Options

Pass flags through the pipe with `-s --`:

```bash
# a specific version
curl -fsSL https://rayucode.com/install | bash -s -- --version 2.2.19

# somewhere else, and leave my shell profiles alone
curl -fsSL https://rayucode.com/install | bash -s -- --dir ~/bin --no-modify-path

# install the JavaScript release even if a standalone binary exists
curl -fsSL https://rayucode.com/install | bash -s -- --npm-tarball

# all options
curl -fsSL https://rayucode.com/install | bash -s -- --help
```

| Flag | Meaning |
|------|---------|
| `--version <v>` | Install an exact version |
| `--dir <path>` | Launcher directory (default `~/.rayu/bin`) |
| `--no-modify-path` | Do not touch shell profiles |
| `--npm-tarball` | Skip the standalone binary |
| `--uninstall` | Remove the install |
| `--quiet` | Less output |

On Windows the same options are PowerShell parameters (`-Version`, `-Dir`,
`-NoModifyPath`, `-NpmTarball`, `-Uninstall`, `-Quiet`). Because `irm | iex`
cannot forward arguments, download the script first:

```powershell
irm https://rayucode.com/install.ps1 -OutFile install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Version 2.2.19
```

This applies the execution policy only to that installer process. It also works
when the current window blocks running downloaded `.ps1` files.

## Updating

```bash
rayu update
```

Re-running the original one-liner does exactly the same thing. Prefer
`rayu update` over a package-manager upgrade: it resolves the latest release
once, installs that **exact** version, and verifies what actually landed.

Auto-updates are **off by default** — Rayu tells you when an update exists but
never installs it behind your back. To turn them on, open `/config` and use the
**Auto-update channel** setting; to silence update notices entirely, set
`DISABLE_AUTOUPDATER=1` as an environment toggle.

## Uninstalling

```bash
rayu uninstall
```

Or re-run the installer with `--uninstall`:

```bash
curl -fsSL https://rayucode.com/install | bash -s -- --uninstall
```

On Windows, download the installer and pass `-Uninstall` the same way shown
above.

This removes the Rayu launcher and its `PATH` entry. Your settings and
credentials in `~/.rayu` are kept — delete them with `rm -rf ~/.rayu` if you
want a clean slate.

## Alternatives

### npm (needs Node >= 18)

```bash
npm install -g @rayu-dev/rayu-cli
```

Use a writable global npm prefix. If you hit `EACCES`, point npm at a directory
you own instead of using `sudo`:

```bash
npm config set prefix ~/.npm-global
export PATH="$HOME/.npm-global/bin:$PATH"
```

Run it once without installing anything:

```bash
npx @rayu-dev/rayu-cli
```

### Bun / pnpm / yarn

```bash
bun install -g @rayu-dev/rayu-cli
pnpm add -g @rayu-dev/rayu-cli
yarn global add @rayu-dev/rayu-cli
```

### Linux packages

`.deb` and `.rpm` packages install the binary to `/usr/bin/rayu` system-wide.

### VS Code extension

The RayuCode extension is installed into VS Code itself — from the Marketplace
(`code --install-extension RayuCode.rayucode`) or from
<https://rayucode.com/download>. See
[VS Code Extension](./17-vscode-extension.md).

## Troubleshooting

**`rayu: command not found` right after installing.** The `PATH` change only
applies to new shells. Either open a new terminal or run:

```bash
export PATH="$HOME/.rayu/bin:$PATH"
```

**The installer warns that another `rayu` is earlier on your `PATH`.** An older
`npm install -g` copy is shadowing the new one. Remove it:

```bash
npm uninstall -g @rayu-dev/rayu-cli
```

**Alpine / musl.** Handled automatically: the installer detects musl and uses a
compatible runtime. If no prebuilt release exists for your platform, install
Node yourself (`apk add nodejs`) and re-run.

**Windows: "this installer needs tar.exe".** The JavaScript fallback path uses
`tar.exe`, which ships with Windows 10 1803 and later. On older builds install
Node 22 or newer and use `npm install -g @rayu-dev/rayu-cli` instead.

**`checksum mismatch`.** The download was corrupted or tampered with. Nothing was
installed. Retry; if it persists, report it with the printed hashes.

> Runtime note: full-text search works best with `ripgrep` (`rg`) installed, and
> git features require `git`. Neither is bundled — install them for full
> functionality (Rayu still runs without them, with reduced search and git
> support).

Next: [Quickstart →](./02-quickstart.md)
