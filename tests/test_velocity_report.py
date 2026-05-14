"""Tests for gitlog_digest.velocity_report."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from gitlog_digest.velocity_report import (
    VelocityReport,
    _velocity_bar,
    build_velocity_report,
    format_velocity_section,
)


def make_commit(day: date, subject: str = "msg"):
    c = MagicMock()
    c.date = datetime(day.year, day.month, day.day, 10, 0, 0)
    c.subject = subject
    return c


MON = date(2024, 1, 1)   # Monday
TUE = date(2024, 1, 2)
WED = date(2024, 1, 3)
NEXT_MON = date(2024, 1, 8)


class TestBuildVelocityReport:
    def test_empty_commits_returns_empty_report(self):
        r = build_velocity_report([])
        assert r.daily == {}
        assert r.weekly == {}

    def test_single_commit_daily_count(self):
        r = build_velocity_report([make_commit(MON)])
        assert r.daily[MON] == 1

    def test_two_commits_same_day(self):
        r = build_velocity_report([make_commit(MON), make_commit(MON)])
        assert r.daily[MON] == 2

    def test_weekly_bucket_uses_monday(self):
        r = build_velocity_report([make_commit(WED)])
        assert MON in r.weekly
        assert r.weekly[MON] == 1

    def test_commits_across_two_weeks(self):
        r = build_velocity_report([make_commit(MON), make_commit(NEXT_MON)])
        assert len(r.weekly) == 2

    def test_same_week_commits_aggregated(self):
        r = build_velocity_report([make_commit(MON), make_commit(TUE), make_commit(WED)])
        assert r.weekly[MON] == 3


class TestVelocityReportMethods:
    def _report(self):
        return build_velocity_report(
            [make_commit(MON), make_commit(MON), make_commit(TUE), make_commit(NEXT_MON)]
        )

    def test_peak_day_returns_day_with_most_commits(self):
        r = self._report()
        assert r.peak_day() == MON

    def test_peak_week_returns_week_with_most_commits(self):
        r = self._report()
        assert r.peak_week() == MON  # week of Jan 1 has 3 commits

    def test_average_daily(self):
        r = self._report()
        # 4 commits over 3 distinct days
        assert abs(r.average_daily() - 4 / 3) < 1e-9

    def test_peak_day_none_when_empty(self):
        assert VelocityReport().peak_day() is None

    def test_peak_week_none_when_empty(self):
        assert VelocityReport().peak_week() is None

    def test_average_daily_zero_when_empty(self):
        assert VelocityReport().average_daily() == 0.0


class TestVelocityBar:
    def test_full_bar_when_value_equals_max(self):
        assert _velocity_bar(10, 10, width=4) == "████"

    def test_empty_bar_when_zero_max(self):
        assert _velocity_bar(5, 0, width=4) == "    "

    def test_half_bar(self):
        bar = _velocity_bar(5, 10, width=10)
        assert bar.count("█") == 5
        assert len(bar) == 10


class TestFormatVelocitySection:
    def test_empty_report_returns_empty_string(self):
        assert format_velocity_section(VelocityReport()) == ""

    def test_contains_header(self):
        r = build_velocity_report([make_commit(MON)])
        out = format_velocity_section(r)
        assert "## Commit Velocity" in out

    def test_contains_peak_day(self):
        r = build_velocity_report([make_commit(MON), make_commit(MON)])
        out = format_velocity_section(r)
        assert str(MON) in out

    def test_top_n_limits_rows(self):
        days = [date(2024, 1, i) for i in range(1, 16)]
        commits = [make_commit(d) for d in days]
        r = build_velocity_report(commits)
        out = format_velocity_section(r, top_n=3)
        # Only 3 day rows should appear under "Top days:"
        rows = [l for l in out.splitlines() if l.startswith("    2024")]
        assert len(rows) == 3
