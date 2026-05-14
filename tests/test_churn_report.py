"""Tests for gitlog_digest.churn_report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.churn_report import (
    ChurnEntry,
    _churn_bar,
    build_churn_map,
    format_churn_section,
    top_churned_files,
)


@dataclass
class FakeCommit:
    files_changed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# build_churn_map
# ---------------------------------------------------------------------------

class TestBuildChurnMap:
    def test_empty_commits_returns_empty(self):
        assert build_churn_map([]) == {}

    def test_single_file_counted_once(self):
        commits = [FakeCommit(["foo.py"])]
        result = build_churn_map(commits)
        assert result["foo.py"] == 1

    def test_file_across_multiple_commits(self):
        commits = [FakeCommit(["a.py"]), FakeCommit(["a.py", "b.py"])]
        result = build_churn_map(commits)
        assert result["a.py"] == 2
        assert result["b.py"] == 1

    def test_commit_with_no_files(self):
        commits = [FakeCommit([]), FakeCommit(["x.py"])]
        result = build_churn_map(commits)
        assert result["x.py"] == 1
        assert len(result) == 1


# ---------------------------------------------------------------------------
# top_churned_files
# ---------------------------------------------------------------------------

class TestTopChurnedFiles:
    def test_returns_churn_entries(self):
        commits = [FakeCommit(["a.py"]), FakeCommit(["a.py"]), FakeCommit(["b.py"])]
        result = top_churned_files(commits)
        assert isinstance(result[0], ChurnEntry)

    def test_sorted_descending(self):
        commits = [FakeCommit(["b.py"]), FakeCommit(["a.py"]), FakeCommit(["a.py"])]
        result = top_churned_files(commits)
        assert result[0].filepath == "a.py"
        assert result[0].change_count == 2

    def test_respects_n_limit(self):
        commits = [FakeCommit([f"f{i}.py"]) for i in range(20)]
        result = top_churned_files(commits, n=5)
        assert len(result) <= 5

    def test_empty_commits_returns_empty_list(self):
        assert top_churned_files([]) == []


# ---------------------------------------------------------------------------
# _churn_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_count_equals_max():
    bar = _churn_bar(10, 10, width=10)
    assert bar == "█" * 10


def test_empty_bar_when_count_zero():
    bar = _churn_bar(0, 10, width=10)
    assert bar == "░" * 10


def test_zero_max_returns_empty_string():
    assert _churn_bar(0, 0) == ""


def test_bar_length_equals_width():
    bar = _churn_bar(3, 7, width=15)
    assert len(bar) == 15


# ---------------------------------------------------------------------------
# format_churn_section
# ---------------------------------------------------------------------------

def test_format_empty_returns_empty_string():
    assert format_churn_section([]) == ""


def test_format_contains_header():
    entries = [ChurnEntry("main.py", 5)]
    output = format_churn_section(entries)
    assert "## File Churn" in output


def test_format_shows_filepath():
    entries = [ChurnEntry("src/utils.py", 3)]
    output = format_churn_section(entries)
    assert "src/utils.py" in output


def test_format_shows_change_count():
    entries = [ChurnEntry("app.py", 7)]
    output = format_churn_section(entries)
    assert "7x" in output
