"""CLI helpers for the revert-commit report."""
from __future__ import annotations

import argparse
from typing import List, Sequence

from gitlog_digest.revert_report import build_revert_entries, format_revert_section


def add_revert_flag(parser: argparse.ArgumentParser) -> None:
    """Register --revert / --top-reverts flags on *parser*."""
    parser.add_argument(
        '--revert',
        action='store_true',
        default=False,
        help='Include a revert-commit section in the digest.',
    )
    parser.add_argument(
        '--top-reverts',
        type=int,
        default=10,
        metavar='N',
        help='Maximum number of revert commits to show (default: 10).',
    )


def maybe_render_revert(args: argparse.Namespace, commits: Sequence) -> str:
    """Return the formatted revert section when the flag is active, else ''."""
    if not getattr(args, 'revert', False):
        return ''
    top_n = getattr(args, 'top_reverts', 10)
    entries = build_revert_entries(commits)
    return format_revert_section(entries, top_n=top_n)


def revert_summary_line(commits: Sequence) -> str:
    """One-liner suitable for embedding in a digest header."""
    entries = build_revert_entries(commits)
    count = len(entries)
    if count == 0:
        return 'No revert commits.'
    noun = 'revert' if count == 1 else 'reverts'
    return f"{count} {noun} detected."
