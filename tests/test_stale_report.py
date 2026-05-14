"""Tests for gitlog_digest.stale_report."""

from datetime import date, datetime
from types import SimpleNamespace
from typing import List

import pytest

from gitlog_digest.stale_report import (
    StaleEntry,
    build_stale_map,
    format_stale_section,
    top_stale_files,
)


def make_commit(author: str, dt: date, files: List[str]):
    return SimpleNamespace(
        author=author,
        date=datetime(dt.year, dt.month, dt.day, 12, 0, 0),
        files_changed=files,
    )


AS_OF = date(2024, 6, 1)


def test_empty_commits_returns_empty_map():
    assert build_stale_map([], as_of=AS_OF) == {}


def test_single_file_single_commit():
    commits = [make_commit("alice", date(2024, 5, 1), ["src/main.py"])]
    stale_map = build_stale_map(commits, as_of=AS_OF)
    assert "src/main.py" in stale_map
    entry = stale_map["src/main.py"]
    assert entry.days_stale == 31
    assert entry.last_author == "alice"


def test_picks_most_recent_commit_for_file():
    commits = [
        make_commit("alice", date(2024, 4, 1), ["README.md"]),
        make_commit("bob", date(2024, 5, 20), ["README.md"]),
    ]
    entry = build_stale_map(commits, as_of=AS_OF)["README.md"]
    assert entry.last_author == "bob"
    assert entry.days_stale == 12


def test_multiple_files_tracked_independently():
    commits = [
        make_commit("alice", date(2024, 5, 1), ["a.py", "b.py"]),
        make_commit("bob", date(2024, 5, 25), ["b.py"]),
    ]
    stale_map = build_stale_map(commits, as_of=AS_OF)
    assert stale_map["a.py"].days_stale == 31
    assert stale_map["b.py"].days_stale == 7


def test_top_stale_files_returns_n():
    commits = [
        make_commit("alice", date(2024, 1, 1), ["old.py"]),
        make_commit("bob", date(2024, 5, 30), ["new.py"]),
        make_commit("carol", date(2024, 3, 1), ["mid.py"]),
    ]
    stale_map = build_stale_map(commits, as_of=AS_OF)
    top = top_stale_files(stale_map, n=2)
    assert len(top) == 2
    assert top[0].filepath == "old.py"


def test_top_stale_files_sorted_descending():
    commits = [
        make_commit("alice", date(2024, 5, 30), ["fresh.py"]),
        make_commit("bob", date(2024, 1, 1), ["ancient.py"]),
    ]
    stale_map = build_stale_map(commits, as_of=AS_OF)
    top = top_stale_files(stale_map)
    assert top[0].days_stale >= top[-1].days_stale


def test_format_stale_section_empty():
    assert format_stale_section([]) == ""


def test_format_stale_section_contains_filename():
    entry = StaleEntry("src/old.py", date(2024, 1, 1), 152, "alice")
    output = format_stale_section([entry])
    assert "src/old.py" in output
    assert "alice" in output


def test_format_stale_section_marks_threshold():
    entry = StaleEntry("legacy.py", date(2024, 1, 1), 60, "bob")
    output = format_stale_section([entry], threshold_days=30)
    assert "(!!)" in output


def test_format_stale_section_no_marker_below_threshold():
    entry = StaleEntry("recent.py", date(2024, 5, 25), 7, "carol")
    output = format_stale_section([entry], threshold_days=30)
    assert "(!!)" not in output
