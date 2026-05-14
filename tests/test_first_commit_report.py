"""Tests for gitlog_digest.first_commit_report."""

from datetime import datetime

import pytest

from gitlog_digest.first_commit_report import (
    FirstCommitEntry,
    build_first_commit_map,
    format_first_commit_section,
    new_contributors,
)


def make_commit(author: str, date: str, subject: str = "some work", hash: str = "abc1234"):
    """Minimal stand-in for a Commit object."""
    from types import SimpleNamespace
    return SimpleNamespace(
        author=author,
        date=datetime.fromisoformat(date),
        subject=subject,
        hash=hash,
    )


class TestBuildFirstCommitMap:
    def test_single_author_single_commit(self):
        commits = [make_commit("alice", "2024-01-10")]
        result = build_first_commit_map(commits)
        assert "alice" in result
        assert result["alice"].date == datetime(2024, 1, 10)

    def test_picks_earliest_for_author(self):
        commits = [
            make_commit("alice", "2024-01-15", hash="bbb0001"),
            make_commit("alice", "2024-01-10", hash="aaa0001"),
            make_commit("alice", "2024-01-20", hash="ccc0001"),
        ]
        result = build_first_commit_map(commits)
        assert result["alice"].hash == "aaa0001"

    def test_multiple_authors_independent(self):
        commits = [
            make_commit("alice", "2024-01-10"),
            make_commit("bob", "2024-01-05"),
        ]
        result = build_first_commit_map(commits)
        assert set(result.keys()) == {"alice", "bob"}
        assert result["bob"].date < result["alice"].date

    def test_empty_commits_returns_empty_map(self):
        assert build_first_commit_map([]) == {}

    def test_subject_stored_correctly(self):
        commits = [make_commit("alice", "2024-01-10", subject="init project")]
        result = build_first_commit_map(commits)
        assert result["alice"].subject == "init project"


class TestNewContributors:
    def test_all_new_when_no_known_authors(self):
        commits = [
            make_commit("alice", "2024-01-10"),
            make_commit("bob", "2024-01-11"),
        ]
        entries = new_contributors(commits)
        names = [e.author for e in entries]
        assert "alice" in names and "bob" in names

    def test_excludes_known_authors(self):
        commits = [
            make_commit("alice", "2024-01-10"),
            make_commit("bob", "2024-01-11"),
        ]
        entries = new_contributors(commits, known_authors=["alice"])
        assert [e.author for e in entries] == ["bob"]

    def test_case_insensitive_exclusion(self):
        commits = [make_commit("Alice", "2024-01-10")]
        entries = new_contributors(commits, known_authors=["alice"])
        assert entries == []

    def test_sorted_by_date(self):
        commits = [
            make_commit("bob", "2024-01-15"),
            make_commit("alice", "2024-01-05"),
        ]
        entries = new_contributors(commits)
        assert entries[0].author == "alice"
        assert entries[1].author == "bob"


class TestFormatFirstCommitSection:
    def _entry(self, author="alice", date="2024-01-10", subject="init", hash="abc1234"):
        return FirstCommitEntry(
            author=author,
            hash=hash,
            date=datetime.fromisoformat(date),
            subject=subject,
        )

    def test_empty_list_returns_empty_string(self):
        assert format_first_commit_section([]) == ""

    def test_contains_author_name(self):
        section = format_first_commit_section([self._entry()])
        assert "alice" in section

    def test_contains_short_hash(self):
        section = format_first_commit_section([self._entry(hash="deadbeef123")])
        assert "deadbee" in section

    def test_contains_date(self):
        section = format_first_commit_section([self._entry(date="2024-03-22")])
        assert "2024-03-22" in section

    def test_custom_header(self):
        section = format_first_commit_section(
            [self._entry()], header="### First Timers"
        )
        assert section.startswith("### First Timers")

    def test_multiple_entries_all_present(self):
        entries = [
            self._entry("alice", "2024-01-05"),
            self._entry("bob", "2024-01-10"),
        ]
        section = format_first_commit_section(entries)
        assert "alice" in section
        assert "bob" in section
