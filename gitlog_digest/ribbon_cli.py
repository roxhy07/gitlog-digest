"""CLI integration for the ribbon (badge) report."""
from __future__ import annotations

import argparse
from typing import Sequence

from gitlog_digest.ribbon_report import build_ribbon_map, format_ribbon_section


def add_ribbon_flag(parser: argparse.ArgumentParser) -> None:
    """Add --ribbons flag to an existing argument parser."""
    parser.add_argument(
        "--ribbons",
        action="store_true",
        default=False,
        help="Include contributor achievement ribbons in the digest.",
    )
    parser.add_argument(
        "--top-ribbons",
        type=int,
        default=10,
        metavar="N",
        help="Number of contributors to show in ribbon report (default: 10).",
    )


def maybe_render_ribbons(args: argparse.Namespace, commits: Sequence) -> str:
    """Return rendered ribbon section if --ribbons flag is set, else empty string."""
    if not getattr(args, "ribbons", False):
        return ""
    top_n = getattr(args, "top_ribbons", 10)
    ribbon_map = build_ribbon_map(commits)
    return format_ribbon_section(ribbon_map, top_n=top_n)


def ribbon_summary_line(commits: Sequence) -> str:
    """Return a one-line summary of badge distribution for digest headers."""
    ribbon_map = build_ribbon_map(commits)
    if not ribbon_map:
        return ""
    total_badges = sum(len(e.badges) for e in ribbon_map.values())
    return f"{len(ribbon_map)} contributor(s) earned {total_badges} badge(s)"
