"""CLI integration for the ticket-label report."""

from __future__ import annotations

from typing import Sequence

from gitlog_digest.label_report import build_label_map, format_label_section


def add_label_flag(parser) -> None:
    """Register --labels / --top-labels flags on *parser*."""
    parser.add_argument(
        "--labels",
        action="store_true",
        default=False,
        help="Include a ticket-label reference report in the output.",
    )
    parser.add_argument(
        "--top-labels",
        type=int,
        default=10,
        metavar="N",
        help="Number of top labels to show (default: 10).",
    )


def maybe_render_labels(args, commits: Sequence) -> str:
    """Return the formatted label section if --labels is set, else empty string."""
    if not getattr(args, "labels", False):
        return ""
    n = getattr(args, "top_labels", 10)
    label_map = build_label_map(commits)
    return format_label_section(label_map, n=n)


def label_summary_line(label_map: dict) -> str:
    """One-line summary suitable for embedding in a digest header."""
    total = sum(e.commit_count for e in label_map.values())
    unique = len(label_map)
    if unique == 0:
        return "No ticket labels referenced."
    return f"{unique} unique label(s) referenced across {total} commit(s)."
