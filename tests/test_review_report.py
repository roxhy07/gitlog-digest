"""Tests for gitlog_digest.review_report."""

from __future__ import annotations

import pytest
from gitlog_digest.review_report import (
    ReviewEntry,
    build_review_entries,
    format_review_section,
    _review_bar,
)


def make_commit(author="Alice", subject="fix bug", files=None):
    """Create a minimal fake Commit-like object."""
    from types import SimpleNamespace

    return SimpleNamespace(
        author=author,
        subject=subject,
        files_changed=files or [],
    )


# ---------------------------------------------------------------------------
# _review_bar
# ---------------------------------------------------------------------------

class TestReviewBar:
    def test_full_bar_when_equal(self):
        assert _review_bar(10, 10) == "#" * 20

    def test_empty_bar_when_zero_value(self):
        assert _review_bar(0, 10) == "-" * 20

    def test_zero_max_returns_spaces(self):
        assert _review_bar(0, 0) == " " * 20

    def test_half_bar(self):
        bar = _review_bar(5, 10)
        assert bar.count("#") == 10
        assert bar.count("-") == 10


# ---------------------------------------------------------------------------
# build_review_entries
# ---------------------------------------------------------------------------

class TestBuildReviewEntries:
    def test_empty_commits_returns_empty(self):
        assert build_review_entries([]) == []

    def test_single_author(self):
        commits = [make_commit("Alice", "init", ["a.py"])]
        entries = build_review_entries(commits)
        assert len(entries) == 1
        assert entries[0].author == "Alice"
        assert entries[0].commit_count == 1
        assert entries[0].files_touched == 1

    def test_multiple_commits_same_author(self):
        commits = [
            make_commit("Bob", "feat A", ["x.py"]),
            make_commit("Bob", "feat B", ["y.py", "z.py"]),
        ]
        entries = build_review_entries(commits)
        assert entries[0].commit_count == 2
        assert entries[0].files_touched == 3

    def test_deduplicates_files(self):
        commits = [
            make_commit("Carol", "fix 1", ["shared.py"]),
            make_commit("Carol", "fix 2", ["shared.py"]),
        ]
        entries = build_review_entries(commits)
        assert entries[0].files_touched == 1

    def test_sorted_by_commit_count_descending(self):
        commits = [
            make_commit("Zara", "s1"),
            make_commit("Alice", "s2"),
            make_commit("Alice", "s3"),
        ]
        entries = build_review_entries(commits)
        assert entries[0].author == "Alice"
        assert entries[1].author == "Zara"

    def test_subjects_collected(self):
        commits = [make_commit("Dave", "subject one"), make_commit("Dave", "subject two")]
        entries = build_review_entries(commits)
        assert "subject one" in entries[0].subjects
        assert "subject two" in entries[0].subjects


# ---------------------------------------------------------------------------
# format_review_section
# ---------------------------------------------------------------------------

class TestFormatReviewSection:
    def test_empty_returns_empty_string(self):
        assert format_review_section([]) == ""

    def test_contains_header(self):
        entries = [ReviewEntry("Alice", 3, 5, [])]
        output = format_review_section(entries)
        assert "## Code Review Activity" in output

    def test_contains_author_name(self):
        entries = [ReviewEntry("Alice", 3, 5, [])]
        output = format_review_section(entries)
        assert "Alice" in output

    def test_shows_commit_and_file_counts(self):
        entries = [ReviewEntry("Bob", 7, 12, [])]
        output = format_review_section(entries)
        assert "7 commit(s)" in output
        assert "12 file(s)" in output

    def test_multiple_entries_all_present(self):
        entries = [
            ReviewEntry("Alice", 5, 3, []),
            ReviewEntry("Bob", 2, 1, []),
        ]
        output = format_review_section(entries)
        assert "Alice" in output
        assert "Bob" in output
