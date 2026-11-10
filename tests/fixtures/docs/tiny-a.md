# Tiny A

Tiny A is a miniature RayuCode document used by the foundation tests. It covers installation, authentication, and a very small amount of troubleshooting.

## Install

Install the CLI with one command. The installer downloads a signed binary and puts it on your PATH.

```bash
curl -fsSL https://rayucode.com/install.sh | sh
```

After installation, run `rayu --version` to confirm the binary is available.

## Authentication

Export your API key before the first request. The test key `rayu_sk_live_test` is not a real credential.

```bash
export RAYU_BOT_API_KEY=rayu_sk_live_test
```

Never commit real keys to a repository.

## Troubleshooting

If the gateway replies with HTTP 429, you have hit a rate limit. Wait for the window to reset before retrying.

```text
HTTP/1.1 429 Too Many Requests
```

That is all Tiny A contains.
