"""Report identifying authors who have gone dormant (no commits recently)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class DormantEntry:
    author: str
    last_commit_date: date
    days_since: int
    total_commits: int

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DormantEntry(author={self.author!r}, "
            f"last_commit_date={self.last_commit_date}, "
            f"days_since={self.days_since})"
        )


def build_dormant_map(
    commits,
    reference_date: Optional[date] = None,
    threshold_days: int = 14,
) -> List[DormantEntry]:
    """Return authors whose last commit is older than *threshold_days* ago.

    Args:
        commits: iterable of Commit objects with .author and .date attributes.
        reference_date: the date to measure dormancy from (defaults to today).
        threshold_days: number of days of inactivity before an author is
            considered dormant.
    """
    if reference_date is None:
        reference_date = date.today()

    last_seen: dict[str, date] = {}
    commit_counts: dict[str, int] = {}

    for commit in commits:
        commit_date = (
            commit.date.date()
            if hasattr(commit.date, "date")
            else commit.date
        )
        author = commit.author
        if author not in last_seen or commit_date > last_seen[author]:
            last_seen[author] = commit_date
        commit_counts[author] = commit_counts.get(author, 0) + 1

    cutoff = reference_date - timedelta(days=threshold_days)
    entries = [
        DormantEntry(
            author=author,
            last_commit_date=last_date,
            days_since=(reference_date - last_date).days,
            total_commits=commit_counts[author],
        )
        for author, last_date in last_seen.items()
        if last_date <= cutoff
    ]
    entries.sort(key=lambda e: e.days_since, reverse=True)
    return entries


def format_dormant_section(entries: List[DormantEntry], top_n: int = 10) -> str:
    """Render a plain-text dormant-authors section."""
    if not entries:
        return ""
    lines = ["Dormant Contributors", "-" * 20]
    for entry in entries[:top_n]:
        lines.append(
            f"  {entry.author} — last seen {entry.last_commit_date} "
            f"({entry.days_since}d ago, {entry.total_commits} commits)"
        )
    return "\n".join(lines)
