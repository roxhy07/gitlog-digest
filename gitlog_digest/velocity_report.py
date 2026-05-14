"""Compute and format a commit-velocity report (commits per day/week)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Sequence

from gitlog_digest.git_parser import Commit


@dataclass
class VelocityReport:
    daily: Dict[date, int] = field(default_factory=dict)
    weekly: Dict[date, int] = field(default_factory=dict)  # keyed by week-start (Monday)

    def peak_day(self) -> date | None:
        if not self.daily:
            return None
        return max(self.daily, key=lambda d: self.daily[d])

    def peak_week(self) -> date | None:
        if not self.weekly:
            return None
        return max(self.weekly, key=lambda d: self.weekly[d])

    def average_daily(self) -> float:
        if not self.daily:
            return 0.0
        return sum(self.daily.values()) / len(self.daily)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"VelocityReport(days={len(self.daily)}, "
            f"weeks={len(self.weekly)}, "
            f"avg_daily={self.average_daily():.1f})"
        )


def build_velocity_report(commits: Sequence[Commit]) -> VelocityReport:
    """Aggregate commits into daily and weekly buckets."""
    daily: Dict[date, int] = defaultdict(int)
    weekly: Dict[date, int] = defaultdict(int)

    for commit in commits:
        d = commit.date.date() if hasattr(commit.date, "date") else commit.date
        daily[d] += 1
        # ISO week starts on Monday
        week_start = d - timedelta(days=d.weekday())
        weekly[week_start] += 1

    return VelocityReport(daily=dict(daily), weekly=dict(weekly))


def _velocity_bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = round(value / max_value * width)
    return "█" * filled + "░" * (width - filled)


def format_velocity_section(report: VelocityReport, top_n: int = 7) -> str:
    """Return a plain-text velocity section."""
    if not report.daily:
        return ""

    lines: List[str] = ["## Commit Velocity"]
    lines.append(f"  Average commits/day : {report.average_daily():.1f}")

    peak = report.peak_day()
    if peak:
        lines.append(f"  Peak day            : {peak} ({report.daily[peak]} commits)")

    peak_w = report.peak_week()
    if peak_w:
        lines.append(f"  Peak week           : {peak_w} ({report.weekly[peak_w]} commits)")

    lines.append("")
    lines.append("  Top days:")
    top_days = sorted(report.daily, key=lambda d: report.daily[d], reverse=True)[:top_n]
    max_val = max(report.daily.values()) if report.daily else 1
    for d in sorted(top_days):
        bar = _velocity_bar(report.daily[d], max_val)
        lines.append(f"    {d}  {bar}  {report.daily[d]}")

    return "\n".join(lines)
