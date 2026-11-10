"""Display titles for the frozen docs, mirrored from ``rayu-web``.

Source: ``app/(main)/docs/docsNav.ts`` in ``rayu-web`` at commit
``486bab47797719a893e6aae9b9363460cd7f9cce``. This module is pure data plus a
lookup helper, so it is implemented in the scaffold (no algorithms here).

Owner: Nike.
"""

from __future__ import annotations

#: Exact sidebar titles for the 14 frozen documents.
DOC_TITLES: dict[str, str] = {
    "01-installation": "Installation",
    "02-quickstart": "Quickstart",
    "03-providers": "Providers",
    "04-models": "Models",
    "05-configuration": "Configuration",
    "06-cli-reference": "CLI reference",
    "07-slash-commands": "Slash commands",
    "10-troubleshooting": "Troubleshooting",
    "15-api-keys": "API keys and the Rayu API",
    "17-vscode-extension": "VS Code extension",
    "18-subscription-plans": "Subscription plans",
    "19-credits-and-limits": "Credits and limits",
    "20-how-token-credit-charge": "How tokens are charged",
    "21-policies": "Policies",
}

__all__ = ["DOC_TITLES", "doc_title"]


def doc_title(slug: str, fallback: str) -> str:
    """Return the sidebar title for *slug*, or *fallback* when unlisted.

    Mirrors ``docTitle(slug, fallback)`` from ``docsNav.ts``.
    """

    return DOC_TITLES.get(slug, fallback)
