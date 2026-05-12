"""Handles writing rendered digest output to stdout or a file."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def write_output(content: str, path: Optional[str] = None) -> None:
    """Write *content* to *path* if given, otherwise to stdout."""
    if path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"Digest written to {dest}", file=sys.stderr)


def choose_extension(fmt: str) -> str:
    """Return a sensible file extension for the given format name."""
    return ".md" if fmt == "markdown" else ".txt"


def default_output_path(since: str, until: str, fmt: str) -> str:
    """Build a default output filename from the date range and format."""
    ext = choose_extension(fmt)
    return f"digest_{since}_{until}{ext}"
