"""CLI helpers for the scope report."""

from __future__ import annotations

from typing import List

from gitlog_digest.scope_report import (
    ScopeEntry,
    build_scope_map,
    format_scope_section,
    top_n_scopes,
)


def add_scope_flag(parser) -> None:
    """Attach ``--scope-report`` and ``--top-scopes`` flags to *parser*."""
    parser.add_argument(
        "--scope-report",
        action="store_true",
        default=False,
        help="Include a breakdown of conventional-commit scopes.",
    )
    parser.add_argument(
        "--top-scopes",
        type=int,
        default=10,
        metavar="N",
        help="Number of top scopes to display (default: 10).",
    )


def maybe_render_scope(args, commits: list) -> str:
    """Return the rendered scope section if the flag is set, else empty string."""
    if not getattr(args, "scope_report", False):
        return ""
    n = getattr(args, "top_scopes", 10)
    scope_map = build_scope_map(commits)
    entries = top_n_scopes(scope_map, n=n)
    return format_scope_section(entries)


def scope_summary_line(entries: List[ScopeEntry]) -> str:
    """Return a one-line summary suitable for a digest header."""
    if not entries:
        return "No conventional-commit scopes detected."
    top = entries[0]
    return (
        f"{len(entries)} scope(s) found; "
        f"busiest: '{top.scope}' ({top.count} commit(s))"
    )
