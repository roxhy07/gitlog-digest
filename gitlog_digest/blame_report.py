"""Formats blame summaries for inclusion in the weekly digest."""

from __future__ import annotations

from typing import List

from gitlog_digest.blame import FileBlame


def _ownership_bar(counts: dict, width: int = 20) -> str:
    """Return a simple ASCII bar showing author proportions."""
    total = sum(counts.values())
    if total == 0:
        return ""
    parts = []
    for author, n in sorted(counts.items(), key=lambda x: -x[1]):
        filled = max(1, round(n / total * width))
        initials = (author.split()[0][0] if author else "?").upper()
        parts.append(initials * filled)
    bar = "".join(parts)
    return bar[:width].ljust(width)


def format_blame_row(fb: FileBlame, max_path: int = 40) -> str:
    """Return a single formatted line for one FileBlame."""
    path = fb.path if len(fb.path) <= max_path else "..." + fb.path[-(max_path - 3):]
    top = fb.top_author or "—"
    bar = _ownership_bar(fb.line_counts)
    return f"  {path:<{max_path}}  {top:<20}  [{bar}]"


def format_blame_section(blames: List[FileBlame], title: str = "File Ownership") -> str:
    """Return a formatted multi-line section for a list of FileBlame objects."""
    if not blames:
        return ""

    header = f"### {title}\n"
    col_heads = f"  {'File':<40}  {'Top Author':<20}  Ownership"
    separator = "  " + "-" * 40 + "  " + "-" * 20 + "  " + "-" * 22
    rows = [format_blame_row(fb) for fb in blames]
    return "\n".join([header, col_heads, separator] + rows) + "\n"


def top_n_files(blames: List[FileBlame], n: int = 5) -> List[FileBlame]:
    """Return the *n* files with the most total lines (descending)."""
    return sorted(blames, key=lambda fb: fb.total_lines, reverse=True)[:n]
