"""Tests for gitlog_digest.contributor_stats."""

from __future__ import annotations

import pytest

from gitlog_digest.contributor_stats import (
    ContributorStats,
    build_contributor_stats,
    rank_contributors,
)


def make_commit(
    author="Alice",
    subject="fix: something",
    files_changed=None,
    lines_added=0,
    lines_deleted=0,
):
    from types import SimpleNamespace

    return SimpleNamespace(
        author=author,
        subject=subject,
        files_changed=files_changed or [],
        lines_added=lines_added,
        lines_deleted=lines_deleted,
    )


class TestContributorStats:
    def test_net_lines_positive(self):
        cs = ContributorStats("Alice", lines_added=10, lines_deleted=3)
        assert cs.net_lines == 7

    def test_net_lines_negative(self):
        cs = ContributorStats("Bob", lines_added=2, lines_deleted=8)
        assert cs.net_lines == -6

    def test_unique_files_deduplicates(self):
        cs = ContributorStats("Alice", files_touched=["a.py", "b.py", "a.py"])
        assert cs.unique_files == 2

    def test_unique_files_empty(self):
        cs = ContributorStats("Alice")
        assert cs.unique_files == 0


class TestBuildContributorStats:
    def test_empty_commits_returns_empty(self):
        assert build_contributor_stats([]) == {}

    def test_single_commit(self):
        commits = [make_commit("Alice", files_changed=["x.py"], lines_added=5)]
        stats = build_contributor_stats(commits)
        assert "Alice" in stats
        assert stats["Alice"].commit_count == 1
        assert stats["Alice"].lines_added == 5

    def test_multiple_commits_same_author(self):
        commits = [
            make_commit("Bob", lines_added=3, lines_deleted=1),
            make_commit("Bob", lines_added=7, lines_deleted=2),
        ]
        stats = build_contributor_stats(commits)
        assert stats["Bob"].commit_count == 2
        assert stats["Bob"].lines_added == 10
        assert stats["Bob"].lines_deleted == 3

    def test_multiple_authors(self):
        commits = [make_commit("Alice"), make_commit("Bob"), make_commit("Alice")]
        stats = build_contributor_stats(commits)
        assert stats["Alice"].commit_count == 2
        assert stats["Bob"].commit_count == 1

    def test_files_accumulated(self):
        commits = [
            make_commit("Alice", files_changed=["a.py", "b.py"]),
            make_commit("Alice", files_changed=["a.py"]),
        ]
        stats = build_contributor_stats(commits)
        assert stats["Alice"].unique_files == 2
        assert len(stats["Alice"].files_touched) == 3


class TestRankContributors:
    def _stats(self):
        return {
            "Alice": ContributorStats("Alice", commit_count=5, lines_added=100),
            "Bob": ContributorStats("Bob", commit_count=2, lines_added=300),
            "Carol": ContributorStats("Carol", commit_count=8, lines_added=50),
        }

    def test_rank_by_commit_count(self):
        ranked = rank_contributors(self._stats(), by="commit_count")
        assert [s.author for s in ranked] == ["Carol", "Alice", "Bob"]

    def test_rank_by_lines_added(self):
        ranked = rank_contributors(self._stats(), by="lines_added")
        assert ranked[0].author == "Bob"

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError, match="'by' must be one of"):
            rank_contributors(self._stats(), by="invalid_field")

    def test_empty_stats(self):
        assert rank_contributors({}) == []
