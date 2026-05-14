"""CLI helpers to integrate topic report into the main digest output."""
from __future__ import annotations

from typing import List, Optional

from gitlog_digest.topic_report import build_topic_map, format_topic_report


def add_topic_flag(parser) -> None:
    """Register --topic-breakdown flag on an argparse parser."""
    parser.add_argument(
        "--topic-breakdown",
        action="store_true",
        default=False,
        help="Include a conventional-commit topic breakdown in the digest.",
    )
    parser.add_argument(
        "--topic-top-n",
        type=int,
        default=10,
        metavar="N",
        help="Maximum number of topic rows to display (default: 10).",
    )


def maybe_render_topic(args, commits: List) -> str:
    """Return the topic section string if the flag is set, otherwise empty string."""
    if not getattr(args, "topic_breakdown", False):
        return ""
    top_n = getattr(args, "topic_top_n", 10)
    buckets = build_topic_map(commits)
    return format_topic_report(buckets, top_n=top_n)


def topic_summary_line(commits: List) -> Optional[str]:
    """Return a one-line summary of topic distribution, or None if no commits."""
    if not commits:
        return None
    buckets = build_topic_map(commits)
    top = sorted(buckets.values(), key=lambda b: b.count, reverse=True)
    parts = [f"{b.label}:{b.count}" for b in top[:4]]
    return "Topics — " + "  ".join(parts)
