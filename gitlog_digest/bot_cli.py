"""CLI helpers for the bot-commit report."""
from __future__ import annotations

import argparse
from typing import Sequence

from gitlog_digest.bot_report import build_bot_map, format_bot_section


def add_bot_flag(parser: argparse.ArgumentParser) -> None:
    """Register --bots / --top-bots flags on *parser*."""
    parser.add_argument(
        "--bots",
        action="store_true",
        default=False,
        help="Include a section listing bot/automated commits.",
    )
    parser.add_argument(
        "--top-bots",
        type=int,
        default=5,
        metavar="N",
        dest="top_bots",
        help="Number of bot authors to show (default: 5).",
    )


def maybe_render_bots(args: argparse.Namespace, commits: Sequence) -> str:
    """Return the rendered bot section if the flag is set, else empty string."""
    if not getattr(args, "bots", False):
        return ""
    n = getattr(args, "top_bots", 5)
    bot_map = build_bot_map(commits)
    return format_bot_section(bot_map, n=n)


def bot_summary_line(commits: Sequence) -> str:
    """One-liner count of bot commits suitable for a digest header."""
    bot_map = build_bot_map(commits)
    total = sum(e.commit_count for e in bot_map.values())
    if total == 0:
        return ""
    plural = "s" if total != 1 else ""
    return f"{total} automated commit{plural} from {len(bot_map)} bot account(s)"
