"""Parse and summarize diff statistics from git commits."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from gitlog_digest.git_parser import Commit


@dataclass
class DiffStats:
    """Aggregated diff statistics across a set of commits."""

    total_insertions: int = 0
    total_deletions: int = 0
    changed_files: List[str] = field(default_factory=list)

    @property
    def net_lines(self) -> int:
        return self.total_insertions - self.total_deletions

    @property
    def unique_file_count(self) -> int:
        return len(set(self.changed_files))


def parse_numstat_line(line: str) -> tuple[int, int, str] | None:
    """Parse a single line from `git diff --numstat`.

    Returns (insertions, deletions, filename) or None if the line is invalid.
    """
    parts = line.strip().split("\t", 2)
    if len(parts) != 3:
        return None
    ins_raw, del_raw, filename = parts
    try:
        insertions = int(ins_raw)
        deletions = int(del_raw)
    except ValueError:
        # Binary files show '-' instead of numbers
        return None
    return insertions, deletions, filename


def aggregate_diff_stats(commits: List[Commit]) -> DiffStats:
    """Build a DiffStats summary from a list of commits.

    Uses the files_changed list already attached to each Commit object and
    the insertions/deletions attributes when present (they default to 0).
    """
    stats = DiffStats()
    for commit in commits:
        stats.total_insertions += getattr(commit, "insertions", 0)
        stats.total_deletions += getattr(commit, "deletions", 0)
        stats.changed_files.extend(commit.files_changed)
    return stats


def format_diff_stats(stats: DiffStats) -> str:
    """Return a compact human-readable summary line."""
    files = stats.unique_file_count
    ins = stats.total_insertions
    dels = stats.total_deletions
    return (
        f"{files} file{'s' if files != 1 else ''} changed, "
        f"+{ins} insertions, -{dels} deletions "
        f"(net {stats.net_lines:+d})"
    )
