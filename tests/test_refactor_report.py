"""Tests for gitlog_digest.refactor_report."""

from __future__ import annotations

import pytest
from gitlog_digest.refactor_report import (
    RefactorEntry,
    build_refactor_map,
    format_refactor_section,
    is_refactor_commit,
    top_refactorers,
)


class FakeCommit:
    def __init__(self, author: str, subject: str):
        self.author = author
        self.subject = subject


# --- is_refactor_commit ---

def test_refactor_keyword_detected():
    assert is_refactor_commit("refactor: extract helper function") is True


def test_cleanup_keyword_detected():
    assert is_refactor_commit("cleanup old auth code") is True


def test_simplify_detected():
    assert is_refactor_commit("simplify the retry logic") is True


def test_regular_commit_not_detected():
    assert is_refactor_commit("add user login feature") is False


def test_case_insensitive_detection():
    assert is_refactor_commit("Refactor DB layer") is True


# --- build_refactor_map ---

def test_empty_commits_returns_empty_map():
    assert build_refactor_map([]) == {}


def test_single_refactor_commit_tracked():
    commits = [FakeCommit("alice", "refactor: split utils module")]
    result = build_refactor_map(commits)
    assert "alice" in result
    assert result["alice"].count == 1


def test_non_refactor_commits_ignored():
    commits = [
        FakeCommit("alice", "add login page"),
        FakeCommit("alice", "fix typo in README"),
    ]
    assert build_refactor_map(commits) == {}


def test_multiple_commits_same_author():
    commits = [
        FakeCommit("bob", "refactor auth"),
        FakeCommit("bob", "cleanup legacy code"),
    ]
    result = build_refactor_map(commits)
    assert result["bob"].count == 2


def test_subjects_stored_correctly():
    commits = [FakeCommit("carol", "rename config variables")]
    result = build_refactor_map(commits)
    assert "rename config variables" in result["carol"].subjects


# --- top_refactorers ---

def test_top_refactorers_sorted_by_count():
    commits = [
        FakeCommit("alice", "refactor A"),
        FakeCommit("bob", "refactor B"),
        FakeCommit("bob", "cleanup C"),
    ]
    result = top_refactorers(build_refactor_map(commits), n=5)
    assert result[0].author == "bob"


def test_top_refactorers_respects_n():
    commits = [FakeCommit(f"author{i}", "refactor x") for i in range(10)]
    result = top_refactorers(build_refactor_map(commits), n=3)
    assert len(result) == 3


# --- format_refactor_section ---

def test_format_empty_returns_empty_string():
    assert format_refactor_section([]) == ""


def test_format_includes_author_name():
    entry = RefactorEntry(author="dave", subjects=["refactor: tidy up"])
    output = format_refactor_section([entry])
    assert "dave" in output


def test_format_shows_subject():
    entry = RefactorEntry(author="eve", subjects=["cleanup old tests"])
    output = format_refactor_section([entry])
    assert "cleanup old tests" in output


def test_format_truncates_long_subject_list():
    subjects = [f"refactor step {i}" for i in range(6)]
    entry = RefactorEntry(author="frank", subjects=subjects)
    output = format_refactor_section([entry])
    assert "and" in output and "more" in output
