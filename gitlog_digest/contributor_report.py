"""Format contributor stats into human-readable report sections."""

from __future__ import annotations

from typing import List, Sequence

from gitlog_digest.contributor_stats import ContributorStats, rank_contributors

_BAR_WIDTH = 20


def _activity_bar(value: int, max_value: int, width: int = _BAR_WIDTH) -> str:
    """Return a simple ASCII bar proportional to *value* / *max_value*."""
    if max_value == 0:
        filled = 0
    else:
        filled = round(width * value / max_value)
    return "█" * filled + "░" * (width - filled)


def format_contributor_row(cs: ContributorStats, max_commits: int) -> str:
    bar = _activity_bar(cs.commit_count, max_commits)
    return (
        f"  {cs.author:<20} {bar}  "
        f"{cs.commit_count:>3} commits  "
        f"+{cs.lines_added}/-{cs.lines_deleted}  "
        f"{cs.unique_files} files"
    )


def format_contributor_section(
    stats_map: dict,
    top_n: int = 10,
    sort_by: str = "commit_count",
) -> str:
    """Return a formatted text block listing top contributors."""
    ranked: List[ContributorStats] = rank_contributors(stats_map, by=sort_by)[:top_n]
    if not ranked:
        return ""
    max_commits = ranked[0].commit_count if sort_by == "commit_count" else max(
        s.commit_count for s in ranked
    )
    lines = ["## Top Contributors", ""]
    for cs in ranked:
        lines.append(format_contributor_row(cs, max_commits))
    lines.append("")
    return "\n".join(lines)
