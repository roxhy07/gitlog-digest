"""File churn report: identifies files changed most frequently across commits."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class ChurnEntry:
    filepath: str
    change_count: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"ChurnEntry({self.filepath!r}, changes={self.change_count})"


def build_churn_map(commits: Sequence) -> Counter:
    """Return a Counter mapping filepath -> number of commits that touched it."""
    counter: Counter = Counter()
    for commit in commits:
        for f in getattr(commit, "files_changed", []):
            counter[f] += 1
    return counter


def top_churned_files(commits: Sequence, n: int = 10) -> List[ChurnEntry]:
    """Return up to *n* ChurnEntry objects sorted by change count descending."""
    counter = build_churn_map(commits)
    return [
        ChurnEntry(filepath=fp, change_count=cnt)
        for fp, cnt in counter.most_common(n)
    ]


def _churn_bar(count: int, max_count: int, width: int = 20) -> str:
    """Render a simple ASCII bar proportional to *count* / *max_count*."""
    if max_count == 0:
        return ""
    filled = round(width * count / max_count)
    return "█" * filled + "░" * (width - filled)


def format_churn_section(entries: List[ChurnEntry], width: int = 20) -> str:
    """Format a plain-text churn section suitable for inclusion in a digest."""
    if not entries:
        return ""
    max_count = entries[0].change_count  # already sorted descending
    lines = ["## File Churn", ""]
    for entry in entries:
        bar = _churn_bar(entry.change_count, max_count, width)
        lines.append(f"  {bar} {entry.change_count:>4}x  {entry.filepath}")
    lines.append("")
    return "\n".join(lines)
