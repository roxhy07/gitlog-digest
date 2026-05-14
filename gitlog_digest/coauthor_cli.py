"""CLI helpers for the co-author collaboration report."""
from __future__ import annotations

import argparse
from typing import List

from gitlog_digest.coauthor_report import (
    build_coauthor_map,
    top_pairs,
    format_coauthor_section,
    CoAuthorPair,
)

_DEFAULT_TOP_N = 10


def add_coauthor_flag(parser: argparse.ArgumentParser) -> None:
    """Register --coauthors flag and --coauthors-top-n on *parser*."""
    parser.add_argument(
        "--coauthors",
        action="store_true",
        default=False,
        help="Include a co-author collaboration section in the digest.",
    )
    parser.add_argument(
        "--coauthors-top-n",
        type=int,
        default=_DEFAULT_TOP_N,
        metavar="N",
        help=f"Number of top co-author pairs to show (default: {_DEFAULT_TOP_N}).",
    )


def maybe_render_coauthors(args: argparse.Namespace, commits) -> str:
    """Return a formatted co-author section if --coauthors was requested."""
    if not getattr(args, "coauthors", False):
        return ""
    top_n: int = getattr(args, "coauthors_top_n", _DEFAULT_TOP_N)
    pair_map = build_coauthor_map(commits)
    pairs = top_pairs(pair_map, n=top_n)
    return format_coauthor_section(pairs, top_n=top_n)


def coauthor_summary_line(pairs: List[CoAuthorPair]) -> str:
    """Return a one-line summary suitable for embedding in a digest header."""
    if not pairs:
        return "No co-author pairs found."
    top = pairs[0]
    return (
        f"Top pair: {top.driver} + {top.navigator} "
        f"({top.commit_count} shared commit(s))"
    )
