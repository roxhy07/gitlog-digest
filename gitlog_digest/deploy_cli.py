"""CLI helpers for the deploy report feature."""
from __future__ import annotations

from typing import Any

from gitlog_digest.deploy_report import build_deploy_entries, format_deploy_section


def add_deploy_flag(parser: Any) -> None:
    """Register --deploy / --top-deploys flags on *parser*."""
    parser.add_argument(
        "--deploy",
        action="store_true",
        default=False,
        help="Include a deployment / release commit section in the digest.",
    )
    parser.add_argument(
        "--top-deploys",
        type=int,
        default=10,
        metavar="N",
        help="Maximum number of deploy commits to list (default: 10).",
    )


def maybe_render_deploy(args: Any, commits: list) -> str:
    """Return the formatted deploy section when the flag is set, else empty string."""
    if not getattr(args, "deploy", False):
        return ""
    top_n = getattr(args, "top_deploys", 10)
    entries = build_deploy_entries(commits)
    return format_deploy_section(entries, top_n=top_n)


def deploy_summary_line(commits: list) -> str:
    """Return a one-liner count of deploy commits suitable for a summary table."""
    entries = build_deploy_entries(commits)
    n = len(entries)
    noun = "commit" if n == 1 else "commits"
    return f"Deployments / releases: {n} {noun}"
