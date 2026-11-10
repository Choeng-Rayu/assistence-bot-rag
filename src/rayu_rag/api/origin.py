"""Origin check, mirrored from ``lib/supportBot/origin.ts``.

Owner: Reach.
"""

from __future__ import annotations

__all__ = ["is_allowed_origin"]


def is_allowed_origin(
    origin: str | None,
    host: str | None,
    forwarded_host: str | None,
    extra_allowlist: str | None = None,
) -> bool:
    """Return whether a request's ``Origin`` header is allowed.

    A missing origin is allowed (curl, same-origin fetches without the header).
    When present, it must match the request ``Host`` / ``X-Forwarded-Host``
    (first value, default ports 443/80) or an entry in *extra_allowlist*
    (comma-separated origins). Invalid origins are rejected.

    TODO(Reach): implement the origin allowlist check.
    """

    raise NotImplementedError("TODO(Reach): implement is_allowed_origin")
