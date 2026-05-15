"""CLI helpers for the fixup/squash/WIP commit report."""
from __future__ import annotations

from typing import List

from gitlog_digest.fixup_report import build_fixup_entries, format_fixup_section


def add_fixup_flag(parser) -> None:
    """Register --fixup flag on *parser*."""
    parser.add_argument(
        "--fixup",
        action="store_true",
        default=False,
        help="Include a section listing fixup/squash/WIP commits.",
    )
    parser.add_argument(
        "--top-fixups",
        type=int,
        default=10,
        metavar="N",
        dest="top_fixups",
        help="Maximum number of fixup commits to show (default: 10).",
    )


def maybe_render_fixup(args, commits: List) -> str:
    """Return the rendered fixup section when the flag is set, else empty string."""
    if not getattr(args, "fixup", False):
        return ""
    entries = build_fixup_entries(commits)
    return format_fixup_section(entries, top_n=args.top_fixups)


def fixup_summary_line(commits: List) -> str:
    """One-line summary suitable for embedding in a digest header."""
    entries = build_fixup_entries(commits)
    if not entries:
        return ""
    kinds = {}
    for e in entries:
        kinds[e.kind] = kinds.get(e.kind, 0) + 1
    parts = [f"{v} {k}" for k, v in sorted(kinds.items())]
    return "Fixup commits: " + ", ".join(parts)
