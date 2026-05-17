"""Tests for gitlog_digest.ribbon_report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from gitlog_digest.ribbon_report import (
    RibbonEntry,
    _assign_badges,
    build_ribbon_map,
    format_ribbon_section,
)


@dataclass
class FakeDiffStats:
    additions: int = 0
    deletions: int = 0


@dataclass
class FakeCommit:
    author: str
    files_changed: List[str] = field(default_factory=list)
    diff_stats: Optional[FakeDiffStats] = None


# --- _assign_badges ---

def test_prolific_committer_badge():
    badges = _assign_badges("alice", 50, 0, 0)
    assert "Prolific Committer" in badges


def test_active_contributor_badge():
    badges = _assign_badges("bob", 10, 0, 0)
    assert "Active Contributor" in badges


def test_file_wrangler_badge():
    badges = _assign_badges("carol", 1, 100, 0)
    assert "File Wrangler" in badges


def test_code_grower_badge():
    badges = _assign_badges("dave", 1, 0, 1000)
    assert "Code Grower" in badges


def test_code_trimmer_badge():
    badges = _assign_badges("eve", 1, 0, -500)
    assert "Code Trimmer" in badges


def test_first_step_badge():
    badges = _assign_badges("frank", 1, 0, 0)
    assert "First Step" in badges


def test_participant_badge_when_no_other():
    badges = _assign_badges("grace", 3, 5, 10)
    assert "Participant" in badges


def test_multiple_badges_can_be_assigned():
    badges = _assign_badges("heidi", 50, 100, 1000)
    assert len(badges) >= 3


# --- build_ribbon_map ---

def test_empty_commits_returns_empty_map():
    assert build_ribbon_map([]) == {}


def test_single_author_gets_entry():
    commits = [FakeCommit(author="alice")]
    result = build_ribbon_map(commits)
    assert "alice" in result
    assert isinstance(result["alice"], RibbonEntry)


def test_multiple_authors_each_get_entry():
    commits = [
        FakeCommit(author="alice"),
        FakeCommit(author="bob"),
    ]
    result = build_ribbon_map(commits)
    assert "alice" in result
    assert "bob" in result


def test_diff_stats_influence_badges():
    commits = [FakeCommit(author="alice", diff_stats=FakeDiffStats(additions=2000, deletions=0))]
    result = build_ribbon_map(commits)
    assert "Code Grower" in result["alice"].badges


def test_files_changed_counted_uniquely():
    commits = [
        FakeCommit(author="alice", files_changed=["a.py", "b.py"]),
        FakeCommit(author="alice", files_changed=["a.py", "c.py"]),
    ]
    result = build_ribbon_map(commits)
    # 3 unique files, not 4
    assert result["alice"] is not None


# --- format_ribbon_section ---

def test_empty_map_returns_empty_string():
    assert format_ribbon_section({}) == ""


def test_section_contains_header():
    ribbon_map = {"alice": RibbonEntry(author="alice", badges=["Participant"])}
    output = format_ribbon_section(ribbon_map)
    assert "Ribbons" in output


def test_section_contains_author_name():
    ribbon_map = {"alice": RibbonEntry(author="alice", badges=["Participant"])}
    output = format_ribbon_section(ribbon_map)
    assert "alice" in output


def test_section_contains_badge_name():
    ribbon_map = {"alice": RibbonEntry(author="alice", badges=["Code Grower"])}
    output = format_ribbon_section(ribbon_map)
    assert "Code Grower" in output


def test_top_n_limits_output():
    ribbon_map = {
        f"author{i}": RibbonEntry(author=f"author{i}", badges=["Participant"])
        for i in range(20)
    }
    output = format_ribbon_section(ribbon_map, top_n=5)
    # Only 5 authors should appear
    author_lines = [l for l in output.splitlines() if l.startswith("-")]
    assert len(author_lines) == 5
