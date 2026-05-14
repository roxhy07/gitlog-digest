"""CLI helpers for the --velocity flag."""

from __future__ import annotations

import argparse
from typing import Sequence

from gitlog_digest.git_parser import Commit
from gitlog_digest.velocity_report import build_velocity_report, format_velocity_section


def add_velocity_flag(parser: argparse.ArgumentParser) -> None:
    """Register --velocity / --velocity-top-n on *parser*."""
    parser.add_argument(
        "--velocity",
        action="store_true",
        default=False,
        help="Append a commit-velocity section to the digest.",
    )
    parser.add_argument(
        "--velocity-top-n",
        type=int,
        default=7,
        metavar="N",
        help="Number of top days to display in velocity section (default: 7).",
    )


def maybe_render_velocity(args: argparse.Namespace, commits: Sequence[Commit]) -> str:
    """Return formatted velocity section if flag is set, else empty string."""
    if not getattr(args, "velocity", False):
        return ""
    top_n = getattr(args, "velocity_top_n", 7)
    report = build_velocity_report(commits)
    return format_velocity_section(report, top_n=top_n)


def velocity_summary_line(commits: Sequence[Commit]) -> str:
    """One-liner summary suitable for embedding in a digest header."""
    report = build_velocity_report(commits)
    avg = report.average_daily()
    peak = report.peak_day()
    if peak is None:
        return "Velocity: no data"
    return f"Velocity: {avg:.1f} commits/day avg, peak {peak} ({report.daily[peak]})"
