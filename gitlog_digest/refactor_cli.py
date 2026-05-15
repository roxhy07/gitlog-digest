"""CLI integration for the refactor report."""

from __future__ import annotations

from typing import Sequence

from gitlog_digest.refactor_report import (
    build_refactor_map,
    format_refactor_section,
    top_refactorers,
)


def add_refactor_flag(parser) -> None:
    """Add --refactor flag to an argparse parser."""
    parser.add_argument(
        "--refactor",
        action="store_true",
        default=False,
        help="Include a refactor activity section in the digest.",
    )
    parser.add_argument(
        "--top-refactorers",
        type=int,
        default=5,
        metavar="N",
        dest="top_refactorers",
        help="Number of top refactorers to show (default: 5).",
    )


def maybe_render_refactor(args, commits: Sequence) -> str:
    """Return the formatted refactor section if the flag is set, else empty string."""
    if not getattr(args, "refactor", False):
        return ""
    refactor_map = build_refactor_map(commits)
    entries = top_refactorers(refactor_map, n=args.top_refactorers)
    return format_refactor_section(entries, top_n=args.top_refactorers)


def refactor_summary_line(commits: Sequence) -> str:
    """Return a one-line summary of refactor activity."""
    refactor_map = build_refactor_map(commits)
    total = sum(e.count for e in refactor_map.values())
    authors = len(refactor_map)
    if total == 0:
        return "No refactor commits detected."
    return f"{total} refactor commit(s) across {authors} author(s)."
