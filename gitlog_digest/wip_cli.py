"""CLI helpers for the WIP-commit report."""

from __future__ import annotations

from typing import List

from gitlog_digest.wip_report import WipEntry, build_wip_entries, format_wip_section


def add_wip_flag(parser) -> None:
    """Register --wip / --top-wip flags on *parser*."""
    parser.add_argument(
        "--wip",
        action="store_true",
        default=False,
        help="include a WIP / draft commit report",
    )
    parser.add_argument(
        "--top-wip",
        type=int,
        default=10,
        metavar="N",
        help="number of WIP commits to list (default: 10)",
    )


def maybe_render_wip(args, commits) -> str:
    """Return the formatted WIP section when the flag is set, else empty string."""
    if not getattr(args, "wip", False):
        return ""
    top_n = getattr(args, "top_wip", 10)
    entries = build_wip_entries(commits)
    return format_wip_section(entries, top_n=top_n)


def wip_summary_line(entries: List[WipEntry]) -> str:
    """One-line summary suitable for embedding in a digest header."""
    if not entries:
        return ""
    return f"{len(entries)} WIP/draft commit{'s' if len(entries) != 1 else ''} detected"
