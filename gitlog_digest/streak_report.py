"""Compute and format contributor commit streaks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List

from gitlog_digest.git_parser import Commit


@dataclass
class StreakInfo:
    author: str
    current_streak: int = 0
    longest_streak: int = 0
    active_days: List[date] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StreakInfo(author={self.author!r}, "
            f"current={self.current_streak}, longest={self.longest_streak})"
        )


def _extract_dates(commits: List[Commit]) -> List[date]:
    """Return sorted unique commit dates from a list of commits."""
    seen = set()
    for c in commits:
        try:
            seen.add(c.date.date() if hasattr(c.date, "date") else c.date)
        except AttributeError:
            pass
    return sorted(seen)


def compute_streak(dates: List[date]) -> tuple[int, int]:
    """Return (current_streak, longest_streak) given a sorted list of unique dates.

    A "current streak" is only counted if the author's last active day is
    today or yesterday (so a streak isn't immediately broken by the clock
    ticking past midnight).
    """
    if not dates:
        return 0, 0

    today = date.today()
    longest = 1
    current_run = 1

    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # current streak: only counts if last active day is today or yesterday
    last_day = dates[-1]
    if last_day >= today - timedelta(days=1):
        current_streak = 1
        for i in range(len(dates) - 1, 0, -1):
            if dates[i] - dates[i - 1] == timedelta(days=1):
                current_streak += 1
            else:
                break
    else:
        current_streak = 0

    return current_streak, longest


def build_streak_report(commits: List[Commit]) -> Dict[str, StreakInfo]:
    """Build a StreakInfo mapping keyed by author."""
    by_author: Dict[str, List[Commit]] = {}
    for c in commits:
        by_author.setdefault(c.author, []).append(c)

    report: Dict[str, StreakInfo] = {}
    for author, author_commits in by_author.items():
        dates = _extract_dates(author_commits)
        current, longest = compute_streak(dates)
        report[author] = StreakInfo(
            author=author,
            current_streak=current,
            longest_streak=longest,
            active_days=dates,
        )
    return report


def top_contributors(report: Dict[str, StreakInfo], n: int = 3) -> List[StreakInfo]:
    """Return the top *n* contributors ranked by longest streak, then current streak.

    Useful for highlighting standout contributors in a summary digest without
    rendering the full streak section.
    """
    ranked = sorted(
        report.values(),
        key=lambda s: (s.longest_streak, s.current_streak),
        reverse=True,
    )
    return ranked[:n]


def format_streak_section(report: Dict[str, StreakInfo]) -> str:
    """Render streak data as a plain-text section."""
    if not report:
        return ""
    lines = ["## Commit Streaks", ""]
    for info in sorted(report.values(), key=lambda s: s.longest_streak, reverse=True):
        flame = " 🔥" if info.current_streak >= 3 else ""
        lines.append(
            f"  {info.author}: current={info.current_streak}d, "
            f"longest={info.longest_streak}d{flame}"
        )
    lines.append("")
    return "\n".join(lines)
