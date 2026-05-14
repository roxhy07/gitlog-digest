"""Report on commit size distribution (small / medium / large / huge)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

# Thresholds (total lines changed = additions + deletions)
SMALL_MAX = 50
MEDIUM_MAX = 200
LARGE_MAX = 500


@dataclass
class CommitSizeBucket:
    label: str
    threshold_max: int  # exclusive upper bound; -1 means unbounded
    commits: List[object] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.commits)

    def __repr__(self) -> str:  # pragma: no cover
        return f"CommitSizeBucket({self.label!r}, count={self.count})"


def _total_churn(commit) -> int:
    """Return additions + deletions for a commit, or 0 if unavailable."""
    stats = getattr(commit, "diff_stats", None)
    if stats is None:
        return 0
    return getattr(stats, "additions", 0) + getattr(stats, "deletions", 0)


def build_size_buckets(commits: Sequence) -> List[CommitSizeBucket]:
    """Categorise commits into size buckets and return them in order."""
    buckets = [
        CommitSizeBucket("small", SMALL_MAX),
        CommitSizeBucket("medium", MEDIUM_MAX),
        CommitSizeBucket("large", LARGE_MAX),
        CommitSizeBucket("huge", -1),
    ]
    for commit in commits:
        churn = _total_churn(commit)
        for bucket in buckets:
            if bucket.threshold_max == -1 or churn < bucket.threshold_max:
                bucket.commits.append(commit)
                break
    return buckets


def _size_bar(count: int, max_count: int, width: int = 20) -> str:
    if max_count == 0:
        return " " * width
    filled = round(count / max_count * width)
    return "█" * filled + "░" * (width - filled)


def format_size_report(buckets: List[CommitSizeBucket]) -> str:
    """Return a plain-text section summarising commit size distribution."""
    if not any(b.count for b in buckets):
        return ""
    max_count = max(b.count for b in buckets)
    lines = ["## Commit Size Distribution\n"]
    for bucket in buckets:
        bar = _size_bar(bucket.count, max_count)
        lines.append(f"  {bucket.label:<8} {bar} {bucket.count}")
    lines.append("")
    thresholds = f"small <{SMALL_MAX}  medium <{MEDIUM_MAX}  large <{LARGE_MAX}  huge ≥{LARGE_MAX}"
    lines.append(f"  ({thresholds})")
    return "\n".join(lines)
