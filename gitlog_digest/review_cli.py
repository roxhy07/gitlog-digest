"""CLI helpers for the --review flag integration."""

from __future__ import annotations

import argparse
from typing import List

from gitlog_digest.git_parser import Commit
from gitlog_digest.review_report import build_review_entries, format_review_section


def add_review_flag(parser: argparse.ArgumentParser) -> None:
    """Attach the --review flag to an existing argument parser."""
    parser.add_argument(
        "--review",
        action="store_true",
        default=False,
        help="Append a code-review activity section to the digest output.",
    )


def maybe_render_review(commits: List[Commit], args: argparse.Namespace) -> str:
    """Return the formatted review section if --review was requested.

    Returns an empty string when the flag is absent or False.
    """
    if not getattr(args, "review", False):
        return ""
    entries = build_review_entries(commits)
    return format_review_section(entries)


def review_summary_line(commits: List[Commit]) -> str:
    """Return a single-line summary of review activity for log/verbose output."""
    entries = build_review_entries(commits)
    if not entries:
        return "No review activity found."
    top = entries[0]
    return (
        f"Top reviewer: {top.author} "
        f"({top.commit_count} commit(s) across {top.files_touched} file(s))"
    )
