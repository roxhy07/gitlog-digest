"""Tests for gitlog_digest.commit_size_report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pytest

from gitlog_digest.commit_size_report import (
    LARGE_MAX,
    MEDIUM_MAX,
    SMALL_MAX,
    CommitSizeBucket,
    _size_bar,
    _total_churn,
    build_size_buckets,
    format_size_report,
)


@dataclass
class FakeDiffStats:
    additions: int = 0
    deletions: int = 0


@dataclass
class FakeCommit:
    subject: str = "chore: update"
    diff_stats: Optional[FakeDiffStats] = None


def make_commit(additions: int = 0, deletions: int = 0) -> FakeCommit:
    return FakeCommit(diff_stats=FakeDiffStats(additions=additions, deletions=deletions))


# ---------------------------------------------------------------------------
# _total_churn
# ---------------------------------------------------------------------------

def test_total_churn_sums_additions_and_deletions():
    c = make_commit(additions=30, deletions=10)
    assert _total_churn(c) == 40


def test_total_churn_no_diff_stats_returns_zero():
    c = FakeCommit(diff_stats=None)
    assert _total_churn(c) == 0


# ---------------------------------------------------------------------------
# build_size_buckets
# ---------------------------------------------------------------------------

def test_empty_commits_returns_four_empty_buckets():
    buckets = build_size_buckets([])
    assert len(buckets) == 4
    assert all(b.count == 0 for b in buckets)


def test_small_commit_goes_to_small_bucket():
    c = make_commit(additions=10, deletions=5)  # total 15 < SMALL_MAX
    buckets = build_size_buckets([c])
    assert buckets[0].label == "small"
    assert buckets[0].count == 1
    assert all(b.count == 0 for b in buckets[1:])


def test_boundary_commit_at_small_max_goes_to_medium():
    c = make_commit(additions=SMALL_MAX, deletions=0)  # total == SMALL_MAX, not < SMALL_MAX
    buckets = build_size_buckets([c])
    assert buckets[1].label == "medium"
    assert buckets[1].count == 1


def test_large_commit():
    c = make_commit(additions=MEDIUM_MAX + 1, deletions=0)
    buckets = build_size_buckets([c])
    assert buckets[2].label == "large"
    assert buckets[2].count == 1


def test_huge_commit():
    c = make_commit(additions=LARGE_MAX, deletions=0)
    buckets = build_size_buckets([c])
    assert buckets[3].label == "huge"
    assert buckets[3].count == 1


def test_multiple_commits_distributed_correctly():
    commits = [
        make_commit(10, 5),        # small
        make_commit(100, 50),      # medium
        make_commit(300, 100),     # large
        make_commit(600, 200),     # huge
        make_commit(5, 0),         # small
    ]
    buckets = build_size_buckets(commits)
    counts = {b.label: b.count for b in buckets}
    assert counts["small"] == 2
    assert counts["medium"] == 1
    assert counts["large"] == 1
    assert counts["huge"] == 1


# ---------------------------------------------------------------------------
# _size_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_equal():
    bar = _size_bar(10, 10, width=10)
    assert bar == "█" * 10


def test_empty_bar_when_zero_max():
    bar = _size_bar(5, 0, width=10)
    assert bar == " " * 10


def test_partial_bar():
    bar = _size_bar(1, 2, width=10)
    assert len(bar) == 10
    assert "█" in bar
    assert "░" in bar


# ---------------------------------------------------------------------------
# format_size_report
# ---------------------------------------------------------------------------

def test_format_returns_empty_string_for_no_commits():
    buckets = build_size_buckets([])
    assert format_size_report(buckets) == ""


def test_format_contains_header():
    buckets = build_size_buckets([make_commit(5, 0)])
    report = format_size_report(buckets)
    assert "Commit Size Distribution" in report


def test_format_contains_all_labels():
    commits = [
        make_commit(10, 0),
        make_commit(100, 0),
        make_commit(300, 0),
        make_commit(600, 0),
    ]
    buckets = build_size_buckets(commits)
    report = format_size_report(buckets)
    for label in ("small", "medium", "large", "huge"):
        assert label in report


def test_format_shows_threshold_legend():
    buckets = build_size_buckets([make_commit(5, 0)])
    report = format_size_report(buckets)
    assert str(SMALL_MAX) in report
    assert str(MEDIUM_MAX) in report
    assert str(LARGE_MAX) in report
