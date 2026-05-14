"""Tests for gitlog_digest.trend_report."""

from datetime import datetime
from types import SimpleNamespace

import pytest

from gitlog_digest.trend_report import (
    DAY_NAMES,
    TrendReport,
    _hour_block_label,
    build_trend_report,
    format_trend_report,
)


def make_commit(weekday: int, hour: int):
    """weekday: 0=Mon … 6=Sun"""
    dt = datetime(2024, 1, 7 + weekday, hour, 0, 0)  # 2024-01-07 is a Sunday; adjust
    # Use a fixed Monday base: 2024-01-08 is Monday
    dt = datetime(2024, 1, 8 + weekday, hour, 0, 0)
    return SimpleNamespace(date=dt)


class TestHourBlockLabel:
    def test_midnight_block(self):
        assert _hour_block_label(0) == "00:00-04:00"

    def test_noon_block(self):
        assert _hour_block_label(12) == "12:00-16:00"

    def test_late_night(self):
        assert _hour_block_label(23) == "20:00-24:00"

    def test_block_boundary(self):
        assert _hour_block_label(4) == "04:00-08:00"


class TestBuildTrendReport:
    def test_empty_commits_returns_zero_counts(self):
        report = build_trend_report([])
        assert all(v == 0 for v in report.by_weekday.values())
        assert all(v == 0 for v in report.by_hour_block.values())

    def test_all_weekdays_present_in_output(self):
        report = build_trend_report([])
        assert set(report.by_weekday.keys()) == set(DAY_NAMES)

    def test_counts_monday_commits(self):
        commits = [make_commit(0, 9), make_commit(0, 10), make_commit(0, 11)]
        report = build_trend_report(commits)
        assert report.by_weekday["Mon"] == 3

    def test_counts_multiple_days(self):
        commits = [make_commit(0, 9), make_commit(1, 14), make_commit(1, 16)]
        report = build_trend_report(commits)
        assert report.by_weekday["Mon"] == 1
        assert report.by_weekday["Tue"] == 2

    def test_hour_block_counted(self):
        commits = [make_commit(0, 9), make_commit(0, 10)]
        report = build_trend_report(commits)
        assert report.by_hour_block["08:00-12:00"] == 2

    def test_commit_without_date_skipped(self):
        commit = SimpleNamespace(date=None)
        report = build_trend_report([commit])
        assert all(v == 0 for v in report.by_weekday.values())

    def test_all_hour_blocks_present(self):
        report = build_trend_report([])
        assert len(report.by_hour_block) == 6  # 24 / 4


class TestTrendReportMethods:
    def test_busiest_day_returns_max(self):
        report = TrendReport(by_weekday={"Mon": 5, "Tue": 2, "Wed": 8})
        assert report.busiest_day() == "Wed"

    def test_busiest_day_none_when_empty(self):
        report = TrendReport()
        assert report.busiest_day() is None

    def test_busiest_hour_block_none_when_empty(self):
        report = TrendReport()
        assert report.busiest_hour_block() is None


class TestFormatTrendReport:
    def test_empty_report_returns_empty_string(self):
        report = build_trend_report([])
        assert format_trend_report(report) == ""

    def test_contains_weekday_header(self):
        commits = [make_commit(0, 9)]
        report = build_trend_report(commits)
        output = format_trend_report(report)
        assert "By weekday" in output

    def test_contains_hour_block_header(self):
        commits = [make_commit(2, 14)]
        report = build_trend_report(commits)
        output = format_trend_report(report)
        assert "By time of day" in output

    def test_busiest_day_shown_in_output(self):
        commits = [make_commit(4, 10), make_commit(4, 11)]
        report = build_trend_report(commits)
        output = format_trend_report(report)
        assert "Fri" in output
        assert "Most active day" in output
