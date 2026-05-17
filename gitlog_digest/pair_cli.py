"""CLI helpers for the pair-collaboration report."""
from __future__ import annotations

import argparse
from typing import Sequence

from gitlog_digest.pair_report import build_pair_map, format_pair_section, top_pairs


def add_pair_flag(parser: argparse.ArgumentParser) -> None:
    """Register --pairs flag and --top-pairs option onto *parser*."""
    parser.add_argument(
        "--pairs",
        action="store_true",
        default=False,
        help="include collaborating-pairs section in the digest",
    )
    parser.add_argument(
        "--top-pairs",
        type=int,
        default=5,
        metavar="N",
        help="number of top pairs to show (default: 5)",
    )


def maybe_render_pairs(args: argparse.Namespace, commits: Sequence) -> str:
    """Return the formatted pairs section, or an empty string if disabled."""
    if not getattr(args, "pairs", False):
        return ""
    n = getattr(args, "top_pairs", 5)
    pair_map = build_pair_map(commits)
    entries = top_pairs(pair_map, n=n)
    return format_pair_section(entries)


def pair_summary_line(args: argparse.Namespace, commits: Sequence) -> str:
    """Return a one-liner summary suitable for a digest header."""
    if not getattr(args, "pairs", False):
        return ""
    pair_map = build_pair_map(commits)
    count = len(pair_map)
    return f"{count} collaborating pair(s) detected"
