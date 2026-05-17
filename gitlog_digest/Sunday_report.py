"""Sunday report — flags commits made on weekends (Saturday/Sunday)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class WeekendEntry:
    author: str
    commits: List[object] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"WeekendEntry(author={self.author!r}, commits={len(self.commits)})"

    @property
    def count(self) -> int:
        return len(self.commits)


def _is_weekend(commit) -> bool:
    """Return True when the commit timestamp falls on Saturday or Sunday."""
    try:
        dt = datetime.fromisoformat(commit.date)
    except (AttributeError, ValueError):
        return False
    return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def build_weekend_map(commits) -> dict[str, WeekendEntry]:
    """Group weekend commits by author."""
    mapping: dict[str, WeekendEntry] = {}
    for commit in commits:
        if not _is_weekend(commit):
            continue
        entry = mapping.setdefault(commit.author, WeekendEntry(author=commit.author))
        entry.commits.append(commit)
    return mapping


def top_weekend_authors(mapping: dict[str, WeekendEntry], n: int = 5) -> List[WeekendEntry]:
    """Return up to *n* entries sorted by commit count descending."""
    return sorted(mapping.values(), key=lambda e: e.count, reverse=True)[:n]


def _weekend_bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = round(value / max_value * width)
    return "█" * filled + "░" * (width - filled)


def format_weekend_section(entries: List[WeekendEntry], *, width: int = 20) -> str:
    """Render a plain-text table of weekend warriors."""
    if not entries:
        return ""
    max_count = max(e.count for e in entries)
    lines = ["Weekend commits", "-" * 40]
    for e in entries:
        bar = _weekend_bar(e.count, max_count, width)
        lines.append(f"{e.author:<20} {bar} {e.count}")
    return "\n".join(lines)
