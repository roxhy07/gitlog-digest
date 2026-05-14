"""Identify files that haven't been touched recently (stale files)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional


@dataclass
class StaleEntry:
    filepath: str
    last_touched: date
    days_stale: int
    last_author: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StaleEntry({self.filepath!r}, last={self.last_touched}, "
            f"days={self.days_stale}, author={self.last_author!r})"
        )


def build_stale_map(
    commits,
    as_of: Optional[date] = None,
) -> Dict[str, StaleEntry]:
    """Return a mapping of filepath -> StaleEntry for every file seen."""
    if as_of is None:
        as_of = date.today()

    # filepath -> (latest_date, author_at_that_date)
    latest: Dict[str, tuple] = {}

    for commit in commits:
        try:
            commit_date = commit.date.date() if hasattr(commit.date, "date") else commit.date
        except AttributeError:
            continue
        for filepath in getattr(commit, "files_changed", []):
            prev = latest.get(filepath)
            if prev is None or commit_date > prev[0]:
                latest[filepath] = (commit_date, commit.author)

    result: Dict[str, StaleEntry] = {}
    for filepath, (last_date, author) in latest.items():
        days = (as_of - last_date).days
        result[filepath] = StaleEntry(
            filepath=filepath,
            last_touched=last_date,
            days_stale=days,
            last_author=author,
        )
    return result


def top_stale_files(stale_map: Dict[str, StaleEntry], n: int = 10) -> List[StaleEntry]:
    """Return the *n* files that have been untouched the longest."""
    return sorted(stale_map.values(), key=lambda e: e.days_stale, reverse=True)[:n]


def format_stale_section(entries: List[StaleEntry], threshold_days: int = 30) -> str:
    """Render a plain-text stale-file section."""
    if not entries:
        return ""

    lines = ["Stale Files", "-----------"]
    for entry in entries:
        marker = " (!!)" if entry.days_stale >= threshold_days else ""
        lines.append(
            f"  {entry.filepath:<45} {entry.days_stale:>4}d ago  [{entry.last_author}]{marker}"
        )
    return "\n".join(lines) + "\n"
