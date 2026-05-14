"""Tests for gitlog_digest.contributor_report."""

from __future__ import annotations

from gitlog_digest.contributor_stats import ContributorStats
from gitlog_digest.contributor_report import (
    _activity_bar,
    format_contributor_row,
    format_contributor_section,
)


def _cs(author="Alice", commits=5, added=20, deleted=5, files=None):
    cs = ContributorStats(
        author=author,
        commit_count=commits,
        lines_added=added,
        lines_deleted=deleted,
        files_touched=files or ["a.py"],
    )
    return cs


class TestActivityBar:
    def test_full_bar_when_equal(self):
        bar = _activity_bar(10, 10)
        assert bar == "█" * 20

    def test_empty_bar_when_zero_value(self):
        bar = _activity_bar(0, 10)
        assert bar == "░" * 20

    def test_zero_max_returns_empty_bar(self):
        bar = _activity_bar(0, 0)
        assert bar == "░" * 20

    def test_half_bar(self):
        bar = _activity_bar(5, 10)
        assert bar.count("█") == 10
        assert len(bar) == 20


class TestFormatContributorRow:
    def test_contains_author_name(self):
        row = format_contributor_row(_cs("Alice", commits=3), max_commits=3)
        assert "Alice" in row

    def test_contains_commit_count(self):
        row = format_contributor_row(_cs(commits=7), max_commits=10)
        assert "7 commits" in row

    def test_contains_line_stats(self):
        row = format_contributor_row(_cs(added=15, deleted=4), max_commits=5)
        assert "+15" in row
        assert "-4" in row

    def test_contains_file_count(self):
        row = format_contributor_row(_cs(files=["x.py", "y.py"]), max_commits=5)
        assert "2 files" in row


class TestFormatContributorSection:
    def _map(self):
        return {
            "Alice": _cs("Alice", commits=10, added=100),
            "Bob": _cs("Bob", commits=3, added=20),
            "Carol": _cs("Carol", commits=7, added=50),
        }

    def test_empty_map_returns_empty_string(self):
        assert format_contributor_section({}) == ""

    def test_contains_header(self):
        section = format_contributor_section(self._map())
        assert "## Top Contributors" in section

    def test_all_authors_present(self):
        section = format_contributor_section(self._map())
        assert "Alice" in section
        assert "Bob" in section
        assert "Carol" in section

    def test_top_n_limits_output(self):
        section = format_contributor_section(self._map(), top_n=1)
        assert "Alice" in section
        assert "Bob" not in section

    def test_sorted_by_commits_default(self):
        section = format_contributor_section(self._map())
        alice_pos = section.index("Alice")
        carol_pos = section.index("Carol")
        assert alice_pos < carol_pos
