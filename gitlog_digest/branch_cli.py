"""CLI helpers for the branch activity report."""

from __future__ import annotations

from typing import List

from gitlog_digest.branch_report import (
    build_branch_map,
    format_branch_section,
    top_n_branches,
)


def add_branch_flag(parser) -> None:
    """Register --branch-report and --top-branches flags on *parser*."""
    parser.add_argument(
        "--branch-report",
        action="store_true",
        default=False,
        help="Include a branch activity section in the digest.",
    )
    parser.add_argument(
        "--top-branches",
        type=int,
        default=10,
        metavar="N",
        help="Number of branches to show (default: 10).",
    )


def maybe_render_branch(args, commits, repo: str = ".") -> str:
    """Return the formatted branch section if the flag is set, else empty string."""
    if not getattr(args, "branch_report", False):
        return ""
    n = getattr(args, "top_branches", 10)
    branch_map = build_branch_map(commits, repo=repo)
    entries = top_n_branches(branch_map, n=n)
    return format_branch_section(entries)


def branch_summary_line(entries: List) -> str:
    """Return a one-line summary suitable for a digest header."""
    if not entries:
        return ""
    total = sum(e.commit_count for e in entries)
    return f"{len(entries)} branch(es) · {total} commits tracked"
