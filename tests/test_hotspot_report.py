"""Tests for gitlog_digest.hotspot_report."""

from __future__ import annotations

import pytest
from gitlog_digest.hotspot_report import (
    HotspotEntry,
    build_hotspot_map,
    top_hotspots,
    _hotspot_bar,
    format_hotspot_section,
)


class FakeCommit:
    def __init__(self, author: str, files_changed=None):
        self.author = author
        self.files_changed = files_changed or []


# ---------------------------------------------------------------------------
# build_hotspot_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty_map():
    assert build_hotspot_map([]) == {}


def test_single_file_single_commit():
    commits = [FakeCommit("alice", ["src/foo.py"])]
    result = build_hotspot_map(commits)
    assert "src/foo.py" in result
    entry = result["src/foo.py"]
    assert entry.commit_count == 1
    assert entry.author_count == 1
    assert entry.authors == ["alice"]


def test_file_across_multiple_commits_increments_count():
    commits = [
        FakeCommit("alice", ["a.py"]),
        FakeCommit("alice", ["a.py"]),
        FakeCommit("bob", ["a.py"]),
    ]
    result = build_hotspot_map(commits)
    entry = result["a.py"]
    assert entry.commit_count == 3
    assert entry.author_count == 2
    assert sorted(entry.authors) == ["alice", "bob"]


def test_authors_deduplicated():
    commits = [FakeCommit("alice", ["x.py"]), FakeCommit("alice", ["x.py"])]
    result = build_hotspot_map(commits)
    assert result["x.py"].author_count == 1


def test_multiple_files_tracked_independently():
    commits = [
        FakeCommit("alice", ["a.py", "b.py"]),
        FakeCommit("bob", ["b.py"]),
    ]
    result = build_hotspot_map(commits)
    assert result["a.py"].commit_count == 1
    assert result["b.py"].commit_count == 2
    assert result["b.py"].author_count == 2


def test_commit_with_no_files_skipped():
    commits = [FakeCommit("alice", [])]
    assert build_hotspot_map(commits) == {}


# ---------------------------------------------------------------------------
# HotspotEntry.score
# ---------------------------------------------------------------------------

def test_score_is_product_of_commits_and_authors():
    entry = HotspotEntry(filepath="f.py", commit_count=5, author_count=3)
    assert entry.score == 15.0


# ---------------------------------------------------------------------------
# top_hotspots
# ---------------------------------------------------------------------------

def test_top_hotspots_returns_sorted_by_score():
    hotspot_map = {
        "a.py": HotspotEntry("a.py", commit_count=2, author_count=1),  # score 2
        "b.py": HotspotEntry("b.py", commit_count=3, author_count=4),  # score 12
        "c.py": HotspotEntry("c.py", commit_count=1, author_count=1),  # score 1
    }
    top = top_hotspots(hotspot_map, n=2)
    assert top[0].filepath == "b.py"
    assert top[1].filepath == "a.py"


def test_top_hotspots_respects_n():
    hotspot_map = {f"f{i}.py": HotspotEntry(f"f{i}.py", i + 1, 1) for i in range(10)}
    assert len(top_hotspots(hotspot_map, n=3)) == 3


# ---------------------------------------------------------------------------
# _hotspot_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_equal():
    bar = _hotspot_bar(10, 10, width=10)
    assert bar == "█" * 10


def test_empty_bar_when_zero_max():
    bar = _hotspot_bar(5, 0, width=10)
    assert bar == " " * 10


def test_partial_bar():
    bar = _hotspot_bar(5, 10, width=10)
    assert "█" in bar
    assert len(bar) == 10


# ---------------------------------------------------------------------------
# format_hotspot_section
# ---------------------------------------------------------------------------

def test_format_empty_returns_empty_string():
    assert format_hotspot_section([]) == ""


def test_format_contains_filepath():
    entries = [HotspotEntry("src/main.py", commit_count=4, author_count=2, authors=["alice", "bob"])]
    output = format_hotspot_section(entries)
    assert "src/main.py" in output
    assert "4 commits" in output
    assert "2 authors" in output


def test_format_contains_header():
    entries = [HotspotEntry("x.py", 1, 1, ["alice"])]
    output = format_hotspot_section(entries)
    assert "Hotspots" in output
