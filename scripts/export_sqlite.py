#!/usr/bin/env python3
"""Optional demo exporter: chunks/postings -> SQLite.

This is *not* part of the production pipeline. The project stores artifacts as
canonical JSON/JSONL; this script exists only so the course's ``sqlite3`` lab
skill can be demonstrated on the generated corpus.

Owner: Somnang (optional, last priority).
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Export corpus artifacts to a SQLite database for a demo.

    TODO(Somnang): export chunks/postings to SQLite for demos
    """

    raise NotImplementedError("TODO(Somnang): export chunks/postings to SQLite for demos")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
