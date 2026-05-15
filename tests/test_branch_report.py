"""Tests for gitlog_digest/branch_report.py"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from unittest.mock import patch

import pytest

from gitlog_digest.branch_report import (
    BranchEntry,
    _branch_bar,
    build_branch_map,
    fetch_branch_for_commit,
    format_branch_section,
    top_n_branches,
)


@dataclass
class FakeCommit:
    hash: str
    author: str
    files_changed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# BranchEntry
# ---------------------------------------------------------------------------

class TestBranchEntry:
    def test_fields_stored(self):
        entry = BranchEntry(branch="main", commit_count=3, authors=["Alice"])
        assert entry.branch == "main"
        assert entry.commit_count == 3
        assert entry.authors == ["Alice"]

    def test_default_authors_empty(self):
        entry = BranchEntry(branch="dev", commit_count=0)
        assert entry.authors == []


# ---------------------------------------------------------------------------
# _branch_bar
# ---------------------------------------------------------------------------

def test_full_bar_when_equal():
    assert _branch_bar(10, 10, width=10) == "█" * 10


def test_empty_bar_when_zero_value():
    assert _branch_bar(0, 10, width=10) == "░" * 10


def test_zero_max_returns_spaces():
    assert _branch_bar(0, 0, width=8) == " " * 8


# ---------------------------------------------------------------------------
# build_branch_map
# ---------------------------------------------------------------------------

def _fake_branch_lookup(sha, repo="."):
    mapping = {"aaa": "main", "bbb": "main", "ccc": "feature/x"}
    return mapping.get(sha)


def test_build_branch_map_groups_by_branch():
    commits = [
        FakeCommit(hash="aaa", author="Alice"),
        FakeCommit(hash="bbb", author="Bob"),
        FakeCommit(hash="ccc", author="Alice"),
    ]
    with patch(
        "gitlog_digest.branch_report.fetch_branch_for_commit",
        side_effect=_fake_branch_lookup,
    ):
        result = build_branch_map(commits)
    assert "main" in result
    assert "feature/x" in result
    assert result["main"].commit_count == 2
    assert result["feature/x"].commit_count == 1


def test_build_branch_map_deduplicates_authors():
    commits = [
        FakeCommit(hash="aaa", author="Alice"),
        FakeCommit(hash="bbb", author="Alice"),
    ]
    with patch(
        "gitlog_digest.branch_report.fetch_branch_for_commit",
        return_value="main",
    ):
        result = build_branch_map(commits)
    assert result["main"].authors == ["Alice"]


def test_build_branch_map_uses_detached_when_none():
    commits = [FakeCommit(hash="zzz", author="Bot")]
    with patch(
        "gitlog_digest.branch_report.fetch_branch_for_commit",
        return_value=None,
    ):
        result = build_branch_map(commits)
    assert "(detached)" in result


# ---------------------------------------------------------------------------
# top_n_branches
# ---------------------------------------------------------------------------

def test_top_n_branches_sorted_descending():
    bmap = {
        "a": BranchEntry("a", 5),
        "b": BranchEntry("b", 12),
        "c": BranchEntry("c", 1),
    }
    top = top_n_branches(bmap, n=2)
    assert [e.branch for e in top] == ["b", "a"]


def test_top_n_branches_respects_limit():
    bmap = {str(i): BranchEntry(str(i), i) for i in range(20)}
    assert len(top_n_branches(bmap, n=5)) == 5


# ---------------------------------------------------------------------------
# format_branch_section
# ---------------------------------------------------------------------------

def test_format_branch_section_empty_returns_empty():
    assert format_branch_section([]) == ""


def test_format_branch_section_contains_branch_name():
    entries = [BranchEntry("main", 7, ["Alice", "Bob"])]
    output = format_branch_section(entries)
    assert "main" in output
    assert "7" in output
    assert "2 authors" in output


def test_format_branch_section_singular_author():
    entries = [BranchEntry("dev", 1, ["Solo"])]
    output = format_branch_section(entries)
    assert "1 author" in output
    assert "authors" not in output.replace("1 author", "")
