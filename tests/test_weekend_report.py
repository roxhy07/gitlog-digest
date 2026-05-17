"""Tests for gitlog_digest.Sunday_report."""
from __future__ import annotations

import pytest
from gitlog_digest.Sunday_report import (
    WeekendEntry,
    _is_weekend,
    _weekend_bar,
    build_weekend_map,
    format_weekend_section,
    top_weekend_authors,
)


class FakeCommit:
    def __init__(self, author: str, date: str):
        self.author = author
        self.date = date


# ---------------------------------------------------------------------------
# _is_weekend
# ---------------------------------------------------------------------------

def test_saturday_is_weekend():
    c = FakeCommit("alice", "2024-01-06T10:00:00")  # Saturday
    assert _is_weekend(c) is True


def test_sunday_is_weekend():
    c = FakeCommit("alice", "2024-01-07T10:00:00")  # Sunday
    assert _is_weekend(c) is True


def test_monday_is_not_weekend():
    c = FakeCommit("alice", "2024-01-08T10:00:00")  # Monday
    assert _is_weekend(c) is False


def test_friday_is_not_weekend():
    c = FakeCommit("alice", "2024-01-05T23:59:59")  # Friday
    assert _is_weekend(c) is False


def test_bad_date_returns_false():
    c = FakeCommit("alice", "not-a-date")
    assert _is_weekend(c) is False


# ---------------------------------------------------------------------------
# build_weekend_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty_map():
    assert build_weekend_map([]) == {}


def test_weekday_commits_excluded():
    commits = [FakeCommit("alice", "2024-01-08T09:00:00")]  # Monday
    assert build_weekend_map(commits) == {}


def test_weekend_commit_included():
    commits = [FakeCommit("alice", "2024-01-06T09:00:00")]  # Saturday
    mapping = build_weekend_map(commits)
    assert "alice" in mapping
    assert mapping["alice"].count == 1


def test_multiple_authors_tracked_independently():
    commits = [
        FakeCommit("alice", "2024-01-06T10:00:00"),
        FakeCommit("bob", "2024-01-07T11:00:00"),
        FakeCommit("alice", "2024-01-07T12:00:00"),
    ]
    mapping = build_weekend_map(commits)
    assert mapping["alice"].count == 2
    assert mapping["bob"].count == 1


# ---------------------------------------------------------------------------
# top_weekend_authors
# ---------------------------------------------------------------------------

def test_top_authors_sorted_by_count():
    commits = [
        FakeCommit("alice", "2024-01-06T10:00:00"),
        FakeCommit("alice", "2024-01-07T10:00:00"),
        FakeCommit("bob", "2024-01-06T10:00:00"),
    ]
    mapping = build_weekend_map(commits)
    top = top_weekend_authors(mapping, n=5)
    assert top[0].author == "alice"
    assert top[1].author == "bob"


def test_top_n_limits_results():
    commits = [FakeCommit(f"user{i}", "2024-01-06T10:00:00") for i in range(10)]
    mapping = build_weekend_map(commits)
    assert len(top_weekend_authors(mapping, n=3)) == 3


# ---------------------------------------------------------------------------
# _weekend_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_equal():
    assert _weekend_bar(5, 5, width=10) == "█" * 10


def test_empty_bar_when_zero_max():
    assert _weekend_bar(0, 0, width=10) == " " * 10


# ---------------------------------------------------------------------------
# format_weekend_section
# ---------------------------------------------------------------------------

def test_empty_entries_returns_empty_string():
    assert format_weekend_section([]) == ""


def test_section_contains_author_name():
    entry = WeekendEntry(author="alice", commits=[object()])
    result = format_weekend_section([entry])
    assert "alice" in result


def test_section_contains_commit_count():
    entry = WeekendEntry(author="alice", commits=[object(), object()])
    result = format_weekend_section([entry])
    assert "2" in result
