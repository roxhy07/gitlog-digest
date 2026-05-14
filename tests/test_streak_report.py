"""Tests for gitlog_digest.streak_report."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from gitlog_digest.streak_report import (
    StreakInfo,
    _extract_dates,
    compute_streak,
    build_streak_report,
    format_streak_section,
)


def make_commit(author: str, commit_date: date):
    c = MagicMock()
    c.author = author
    c.date = MagicMock()
    c.date.date.return_value = commit_date
    return c


TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


class TestExtractDates:
    def test_returns_sorted_unique_dates(self):
        commits = [
            make_commit("alice", TODAY),
            make_commit("alice", YESTERDAY),
            make_commit("alice", TODAY),  # duplicate
        ]
        result = _extract_dates(commits)
        assert result == sorted({TODAY, YESTERDAY})

    def test_empty_commits_returns_empty(self):
        assert _extract_dates([]) == []


class TestComputeStreak:
    def test_empty_dates_returns_zeros(self):
        assert compute_streak([]) == (0, 0)

    def test_single_day_today_gives_current_one(self):
        current, longest = compute_streak([TODAY])
        assert current == 1
        assert longest == 1

    def test_consecutive_days_ending_today(self):
        days = [TODAY - timedelta(days=i) for i in range(4, -1, -1)]
        current, longest = compute_streak(days)
        assert current == 5
        assert longest == 5

    def test_gap_resets_current_streak(self):
        days = [
            TODAY - timedelta(days=10),
            TODAY - timedelta(days=9),
            TODAY - timedelta(days=8),
            TODAY,
        ]
        current, longest = compute_streak(days)
        assert current == 1
        assert longest == 3

    def test_old_streak_gives_zero_current(self):
        days = [
            date(2024, 1, 1),
            date(2024, 1, 2),
            date(2024, 1, 3),
        ]
        current, longest = compute_streak(days)
        assert current == 0
        assert longest == 3


class TestBuildStreakReport:
    def test_groups_by_author(self):
        commits = [
            make_commit("alice", TODAY),
            make_commit("alice", YESTERDAY),
            make_commit("bob", TODAY),
        ]
        report = build_streak_report(commits)
        assert "alice" in report
        assert "bob" in report

    def test_alice_has_two_active_days(self):
        commits = [
            make_commit("alice", TODAY),
            make_commit("alice", YESTERDAY),
        ]
        report = build_streak_report(commits)
        assert len(report["alice"].active_days) == 2

    def test_empty_commits_returns_empty_dict(self):
        assert build_streak_report([]) == {}


class TestFormatStreakSection:
    def test_empty_report_returns_empty_string(self):
        assert format_streak_section({}) == ""

    def test_contains_header(self):
        report = {"alice": StreakInfo(author="alice", current_streak=1, longest_streak=3)}
        result = format_streak_section(report)
        assert "## Commit Streaks" in result

    def test_shows_author_name(self):
        report = {"bob": StreakInfo(author="bob", current_streak=0, longest_streak=2)}
        result = format_streak_section(report)
        assert "bob" in result

    def test_flame_emoji_for_long_streak(self):
        report = {"alice": StreakInfo(author="alice", current_streak=5, longest_streak=5)}
        result = format_streak_section(report)
        assert "🔥" in result

    def test_no_flame_for_short_streak(self):
        report = {"alice": StreakInfo(author="alice", current_streak=2, longest_streak=2)}
        result = format_streak_section(report)
        assert "🔥" not in result

    def test_sorted_by_longest_streak_descending(self):
        report = {
            "alice": StreakInfo(author="alice", current_streak=1, longest_streak=10),
            "bob": StreakInfo(author="bob", current_streak=1, longest_streak=3),
        }
        result = format_streak_section(report)
        assert result.index("alice") < result.index("bob")
