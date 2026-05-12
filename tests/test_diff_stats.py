"""Tests for gitlog_digest.diff_stats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.diff_stats import (
    DiffStats,
    aggregate_diff_stats,
    format_diff_stats,
    parse_numstat_line,
)


# ---------------------------------------------------------------------------
# Minimal Commit stub so we don't depend on git_parser internals
# ---------------------------------------------------------------------------

@dataclass
class FakeCommit:
    files_changed: List[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0


# ---------------------------------------------------------------------------
# parse_numstat_line
# ---------------------------------------------------------------------------

class TestParseNumstatLine:
    def test_valid_line(self):
        result = parse_numstat_line("10\t3\tsrc/foo.py")
        assert result == (10, 3, "src/foo.py")

    def test_binary_file_returns_none(self):
        assert parse_numstat_line("-\t-\timage.png") is None

    def test_too_few_columns_returns_none(self):
        assert parse_numstat_line("10\t3") is None

    def test_strips_whitespace(self):
        result = parse_numstat_line("  5\t2\tREADME.md  ")
        assert result == (5, 2, "README.md")


# ---------------------------------------------------------------------------
# aggregate_diff_stats
# ---------------------------------------------------------------------------

class TestAggregateDiffStats:
    def test_empty_commits(self):
        stats = aggregate_diff_stats([])
        assert stats.total_insertions == 0
        assert stats.total_deletions == 0
        assert stats.changed_files == []

    def test_sums_insertions_and_deletions(self):
        commits = [
            FakeCommit(insertions=10, deletions=2, files_changed=["a.py"]),
            FakeCommit(insertions=5, deletions=1, files_changed=["b.py"]),
        ]
        stats = aggregate_diff_stats(commits)
        assert stats.total_insertions == 15
        assert stats.total_deletions == 3

    def test_unique_file_count_deduplicates(self):
        commits = [
            FakeCommit(files_changed=["a.py", "b.py"]),
            FakeCommit(files_changed=["a.py", "c.py"]),
        ]
        stats = aggregate_diff_stats(commits)
        assert stats.unique_file_count == 3

    def test_net_lines(self):
        stats = DiffStats(total_insertions=20, total_deletions=8)
        assert stats.net_lines == 12


# ---------------------------------------------------------------------------
# format_diff_stats
# ---------------------------------------------------------------------------

class TestFormatDiffStats:
    def test_basic_output(self):
        stats = DiffStats(
            total_insertions=10,
            total_deletions=4,
            changed_files=["a.py", "b.py"],
        )
        text = format_diff_stats(stats)
        assert "2 files changed" in text
        assert "+10" in text
        assert "-4" in text

    def test_singular_file(self):
        stats = DiffStats(
            total_insertions=1,
            total_deletions=0,
            changed_files=["README.md"],
        )
        assert "1 file changed" in format_diff_stats(stats)

    def test_net_sign_shown(self):
        stats = DiffStats(total_insertions=3, total_deletions=7, changed_files=[])
        assert "net -4" in format_diff_stats(stats)
