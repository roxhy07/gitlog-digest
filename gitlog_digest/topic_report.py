"""Groups commits by topic/prefix (e.g. feat:, fix:, chore:) based on conventional commit style."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

CONVENTIONAL_PREFIXES = [
    "feat", "fix", "chore", "docs", "style",
    "refactor", "perf", "test", "build", "ci", "revert",
]


@dataclass
class TopicBucket:
    label: str
    commits: List = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.commits)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TopicBucket(label={self.label!r}, count={self.count})"


def _extract_prefix(subject: str) -> str:
    """Return the conventional commit prefix, or 'other' if none matched."""
    lower = subject.lower().strip()
    for prefix in CONVENTIONAL_PREFIXES:
        if lower.startswith(prefix + ":") or lower.startswith(prefix + "("):
            return prefix
    return "other"


def build_topic_map(commits) -> Dict[str, TopicBucket]:
    """Bucket commits by their conventional-commit prefix."""
    buckets: Dict[str, TopicBucket] = {}
    for commit in commits:
        label = _extract_prefix(commit.subject)
        if label not in buckets:
            buckets[label] = TopicBucket(label=label)
        buckets[label].commits.append(commit)
    return buckets


def format_topic_report(buckets: Dict[str, TopicBucket], top_n: int = 10) -> str:
    """Render a compact topic breakdown sorted by commit count."""
    if not buckets:
        return ""
    sorted_buckets = sorted(buckets.values(), key=lambda b: b.count, reverse=True)[:top_n]
    max_count = sorted_buckets[0].count if sorted_buckets else 1
    lines = ["### Commits by Topic", ""]
    for bucket in sorted_buckets:
        bar_len = max(1, round((bucket.count / max_count) * 20))
        bar = "█" * bar_len
        lines.append(f"  {bucket.label:<12} {bar:<20}  {bucket.count}")
    lines.append("")
    return "\n".join(lines)
