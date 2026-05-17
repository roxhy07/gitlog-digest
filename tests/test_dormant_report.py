"""Tests for gitlog_digest.dormant_report."""
from datetime import date, datetime

import pytest

from gitlog_digest.dormant_report import (
    DormantEntry,
    build_dormant_map,
    format_dormant_section,
)


class FakeCommit:
    def __init__(self, author: str, commit_date):
        self.author = author
        # Accept both date and datetime to mirror real Commit behaviour.
        self.date = commit_date


REF = date(2024, 6, 1)


def _c(author, d):
    return FakeCommit(author, d)


def test_empty_commits_returns_empty():
    assert build_dormant_map([], reference_date=REF) == []


def test_active_author_not_included():
    commits = [_c("alice", date(2024, 5, 29))]  # only 3 days ago
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert result == []


def test_dormant_author_included():
    commits = [_c("bob", date(2024, 5, 1))]  # 31 days ago
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert len(result) == 1
    assert result[0].author == "bob"
    assert result[0].days_since == 31


def test_days_since_calculated_correctly():
    commits = [_c("carol", date(2024, 5, 10))]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert result[0].days_since == 22


def test_total_commits_counted():
    commits = [
        _c("dave", date(2024, 4, 1)),
        _c("dave", date(2024, 4, 5)),
        _c("dave", date(2024, 4, 10)),
    ]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert result[0].total_commits == 3


def test_last_commit_date_is_most_recent():
    commits = [
        _c("eve", date(2024, 4, 1)),
        _c("eve", date(2024, 4, 20)),
        _c("eve", date(2024, 4, 10)),
    ]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert result[0].last_commit_date == date(2024, 4, 20)


def test_sorted_by_days_since_descending():
    commits = [
        _c("alpha", date(2024, 4, 1)),   # 61 days
        _c("beta", date(2024, 5, 1)),    # 31 days
        _c("gamma", date(2024, 3, 1)),   # 92 days
    ]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert [e.author for e in result] == ["gamma", "alpha", "beta"]


def test_datetime_date_attribute_accepted():
    commits = [FakeCommit("frank", datetime(2024, 4, 15, 9, 0, 0))]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert result[0].last_commit_date == date(2024, 4, 15)


def test_exactly_on_cutoff_included():
    # cutoff = REF - 14 = 2024-05-18; commit on that exact day => included
    commits = [_c("grace", date(2024, 5, 18))]
    result = build_dormant_map(commits, reference_date=REF, threshold_days=14)
    assert len(result) == 1


def test_format_empty_returns_empty_string():
    assert format_dormant_section([]) == ""


def test_format_contains_author_name():
    entries = [
        DormantEntry(author="heidi", last_commit_date=date(2024, 4, 1), days_since=61, total_commits=5)
    ]
    output = format_dormant_section(entries)
    assert "heidi" in output
    assert "61d ago" in output


def test_format_respects_top_n():
    entries = [
        DormantEntry(author=f"user{i}", last_commit_date=date(2024, 3, 1), days_since=90, total_commits=1)
        for i in range(20)
    ]
    output = format_dormant_section(entries, top_n=5)
    assert output.count("user") == 5
