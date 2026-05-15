"""Tests for gitlog_digest.scope_report."""

from __future__ import annotations

import pytest
from gitlog_digest.scope_report import (
    ScopeEntry,
    _extract_scope,
    _scope_bar,
    build_scope_map,
    format_scope_section,
    top_n_scopes,
)


class FakeCommit:
    def __init__(self, subject: str, author: str = "alice"):
        self.subject = subject
        self.author = author


# --- _extract_scope ---

def test_extract_scope_basic():
    assert _extract_scope("feat(auth): add login") == "auth"


def test_extract_scope_no_scope_returns_none():
    assert _extract_scope("fix: correct typo") is None


def test_extract_scope_lowercases():
    assert _extract_scope("Feat(API): something") == "api"


def test_extract_scope_empty_string_returns_none():
    assert _extract_scope("") is None


def test_extract_scope_nested_parens():
    # only captures up to first closing paren
    assert _extract_scope("chore(deps): bump") == "deps"


# --- build_scope_map ---

def test_empty_commits_returns_empty_map():
    assert build_scope_map([]) == {}


def test_single_commit_with_scope():
    commits = [FakeCommit("feat(ui): add button")]
    result = build_scope_map(commits)
    assert "ui" in result
    assert result["ui"].count == 1


def test_commit_without_scope_ignored():
    commits = [FakeCommit("fix: plain fix")]
    assert build_scope_map(commits) == {}


def test_multiple_commits_same_scope_accumulate():
    commits = [
        FakeCommit("feat(auth): login"),
        FakeCommit("fix(auth): token refresh"),
    ]
    result = build_scope_map(commits)
    assert result["auth"].count == 2


def test_authors_deduplicated():
    commits = [
        FakeCommit("feat(api): endpoint", author="alice"),
        FakeCommit("fix(api): null check", author="alice"),
        FakeCommit("chore(api): lint", author="bob"),
    ]
    result = build_scope_map(commits)
    assert sorted(result["api"].authors) == ["alice", "bob"]


def test_different_scopes_tracked_independently():
    commits = [
        FakeCommit("feat(ui): button"),
        FakeCommit("feat(api): route"),
    ]
    result = build_scope_map(commits)
    assert set(result.keys()) == {"ui", "api"}


# --- top_n_scopes ---

def test_top_n_returns_sorted_by_count():
    commits = [
        FakeCommit("feat(api): a"),
        FakeCommit("feat(api): b"),
        FakeCommit("fix(ui): c"),
    ]
    scope_map = build_scope_map(commits)
    top = top_n_scopes(scope_map, n=5)
    assert top[0].scope == "api"
    assert top[1].scope == "ui"


def test_top_n_limits_results():
    commits = [FakeCommit(f"feat(scope{i}): msg") for i in range(20)]
    scope_map = build_scope_map(commits)
    assert len(top_n_scopes(scope_map, n=5)) == 5


# --- _scope_bar ---

def test_full_bar_when_equal():
    assert _scope_bar(10, 10, width=10) == "█" * 10


def test_empty_bar_when_zero_max():
    assert _scope_bar(5, 0, width=10) == " " * 10


# --- format_scope_section ---

def test_format_empty_returns_empty_string():
    assert format_scope_section([]) == ""


def test_format_contains_scope_name():
    entries = [ScopeEntry(scope="auth", count=3)]
    output = format_scope_section(entries)
    assert "auth" in output


def test_format_contains_commit_count():
    entries = [ScopeEntry(scope="ui", count=7)]
    output = format_scope_section(entries)
    assert "7" in output
