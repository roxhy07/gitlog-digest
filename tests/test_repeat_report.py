"""Tests for gitlog_digest.repeat_report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.repeat_report import (
    RepeatEntry,
    _repeat_bar,
    build_repeat_map,
    format_repeat_section,
    top_repeated_files,
)


@dataclass
class FakeCommit:
    author: str
    files_changed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# build_repeat_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty_map():
    assert build_repeat_map([]) == {}


def test_single_file_single_commit():
    commits = [FakeCommit(author="alice", files_changed=["foo.py"])]
    result = build_repeat_map(commits)
    assert "foo.py" in result
    assert result["foo.py"].commit_count == 1
    assert result["foo.py"].authors == ["alice"]


def test_file_across_multiple_commits_counts_correctly():
    commits = [
        FakeCommit(author="alice", files_changed=["foo.py"]),
        FakeCommit(author="bob", files_changed=["foo.py"]),
        FakeCommit(author="alice", files_changed=["foo.py"]),
    ]
    result = build_repeat_map(commits)
    assert result["foo.py"].commit_count == 3


def test_authors_deduplicated_preserving_order():
    commits = [
        FakeCommit(author="alice", files_changed=["bar.py"]),
        FakeCommit(author="bob", files_changed=["bar.py"]),
        FakeCommit(author="alice", files_changed=["bar.py"]),
    ]
    result = build_repeat_map(commits)
    assert result["bar.py"].authors == ["alice", "bob"]


def test_multiple_files_tracked_independently():
    commits = [
        FakeCommit(author="alice", files_changed=["a.py", "b.py"]),
        FakeCommit(author="bob", files_changed=["b.py"]),
    ]
    result = build_repeat_map(commits)
    assert result["a.py"].commit_count == 1
    assert result["b.py"].commit_count == 2


# ---------------------------------------------------------------------------
# top_repeated_files
# ---------------------------------------------------------------------------

def test_top_repeated_files_sorted_descending():
    entries = {
        "a.py": RepeatEntry("a.py", 5, ["alice"]),
        "b.py": RepeatEntry("b.py", 10, ["bob"]),
        "c.py": RepeatEntry("c.py", 2, ["carol"]),
    }
    top = top_repeated_files(entries, n=3)
    assert [e.filepath for e in top] == ["b.py", "a.py", "c.py"]


def test_top_repeated_files_respects_n():
    entries = {f"f{i}.py": RepeatEntry(f"f{i}.py", i, []) for i in range(20)}
    top = top_repeated_files(entries, n=5)
    assert len(top) == 5


# ---------------------------------------------------------------------------
# _repeat_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_equal():
    assert _repeat_bar(10, 10, 10) == "#" * 10


def test_empty_bar_when_zero_max():
    assert _repeat_bar(5, 0, 10) == " " * 10


def test_partial_bar():
    bar = _repeat_bar(5, 10, 20)
    assert bar.count("#") == 10
    assert bar.count("-") == 10


# ---------------------------------------------------------------------------
# format_repeat_section
# ---------------------------------------------------------------------------

def test_format_empty_entries_returns_empty_string():
    assert format_repeat_section([]) == ""


def test_format_includes_filepath():
    entries = [RepeatEntry("hot.py", 7, ["alice", "bob"])]
    output = format_repeat_section(entries)
    assert "hot.py" in output


def test_format_shows_commit_count():
    entries = [RepeatEntry("hot.py", 7, ["alice"])]
    output = format_repeat_section(entries)
    assert "7x" in output


def test_format_truncates_authors_beyond_three():
    authors = ["a", "b", "c", "d", "e"]
    entries = [RepeatEntry("big.py", 5, authors)]
    output = format_repeat_section(entries)
    assert "+2" in output
