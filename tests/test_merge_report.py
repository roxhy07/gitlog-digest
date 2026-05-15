"""Tests for gitlog_digest.merge_report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.merge_report import (
    MergeEntry,
    build_merge_entries,
    format_merge_section,
    is_merge_commit,
    _extract_branches,
)


@dataclass
class FakeCommit:
    hash: str = "abc1234567890"
    author: str = "Alice"
    subject: str = "add feature"
    date: str = "2024-06-01"
    files_changed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# is_merge_commit
# ---------------------------------------------------------------------------


def test_merge_branch_detected():
    assert is_merge_commit("Merge branch 'feature/foo' into main")


def test_merge_pull_request_detected():
    assert is_merge_commit("Merge pull request #42 from org/branch")


def test_merge_remote_tracking_detected():
    assert is_merge_commit("Merge remote-tracking branch 'origin/dev'")


def test_regular_commit_not_detected():
    assert not is_merge_commit("fix: correct off-by-one error")


def test_empty_subject_not_detected():
    assert not is_merge_commit("")


# ---------------------------------------------------------------------------
# _extract_branches
# ---------------------------------------------------------------------------


def test_extract_branches_single_quote():
    result = _extract_branches("Merge branch 'feature/login' into main")
    assert "feature/login" in result


def test_extract_branches_no_quotes_returns_empty():
    result = _extract_branches("Merge pull request #1 from org/branch")
    assert result == []


# ---------------------------------------------------------------------------
# build_merge_entries
# ---------------------------------------------------------------------------


def test_empty_commits_returns_empty():
    assert build_merge_entries([]) == []


def test_non_merge_commits_filtered_out():
    commits = [FakeCommit(subject="feat: new button"), FakeCommit(subject="chore: lint")]
    assert build_merge_entries(commits) == []


def test_merge_commits_included():
    commits = [
        FakeCommit(subject="Merge branch 'dev' into main", hash="aaa000000001"),
        FakeCommit(subject="fix: typo"),
    ]
    result = build_merge_entries(commits)
    assert len(result) == 1
    assert result[0].hash == "aaa000000001"


def test_entry_author_preserved():
    commits = [FakeCommit(subject="Merge branch 'x' into main", author="Bob")]
    result = build_merge_entries(commits)
    assert result[0].author == "Bob"


def test_entry_branches_extracted():
    commits = [FakeCommit(subject="Merge branch 'hotfix/crash' into main")]
    result = build_merge_entries(commits)
    assert "hotfix/crash" in result[0].branches_mentioned


# ---------------------------------------------------------------------------
# format_merge_section
# ---------------------------------------------------------------------------


def test_format_empty_returns_empty_string():
    assert format_merge_section([]) == ""


def test_format_contains_header():
    entry = MergeEntry(hash="abc123", author="Alice", subject="Merge branch 'x' into main", date="2024-06-01")
    output = format_merge_section([entry])
    assert "Merge Commits" in output


def test_format_shows_short_hash():
    entry = MergeEntry(hash="deadbeef1234", author="Alice", subject="Merge branch 'y' into main", date="2024-06-01")
    output = format_merge_section([entry])
    assert "deadbee" in output


def test_format_top_n_limits_output():
    entries = [
        MergeEntry(hash=f"hash{i:06d}", author="A", subject="Merge branch 'b' into main", date="2024-06-01")
        for i in range(20)
    ]
    output = format_merge_section(entries, top_n=3)
    assert output.count("Merge branch") == 3
