"""Per-contributor statistics aggregated across a digest period."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from gitlog_digest.git_parser import Commit


@dataclass
class ContributorStats:
    author: str
    commit_count: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    files_touched: List[str] = field(default_factory=list)

    @property
    def net_lines(self) -> int:
        return self.lines_added - self.lines_deleted

    @property
    def unique_files(self) -> int:
        return len(set(self.files_touched))

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ContributorStats({self.author!r}, commits={self.commit_count}, "
            f"net={self.net_lines:+d})"
        )


def build_contributor_stats(
    commits: Sequence[Commit],
) -> Dict[str, ContributorStats]:
    """Return a mapping of author -> ContributorStats for *commits*."""
    stats: Dict[str, ContributorStats] = {}
    for commit in commits:
        cs = stats.setdefault(commit.author, ContributorStats(author=commit.author))
        cs.commit_count += 1
        cs.lines_added += getattr(commit, "lines_added", 0) or 0
        cs.lines_deleted += getattr(commit, "lines_deleted", 0) or 0
        cs.files_touched.extend(getattr(commit, "files_changed", []) or [])
    return stats


def rank_contributors(
    stats: Dict[str, ContributorStats],
    by: str = "commit_count",
) -> List[ContributorStats]:
    """Return contributor stats sorted descending by *by* field."""
    valid = {"commit_count", "lines_added", "net_lines", "unique_files"}
    if by not in valid:
        raise ValueError(f"'by' must be one of {valid}, got {by!r}")
    return sorted(stats.values(), key=lambda s: getattr(s, by), reverse=True)
