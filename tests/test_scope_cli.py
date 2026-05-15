"""Tests for gitlog_digest.scope_cli."""

from __future__ import annotations

import argparse

import pytest
from gitlog_digest.scope_cli import (
    add_scope_flag,
    maybe_render_scope,
    scope_summary_line,
)
from gitlog_digest.scope_report import ScopeEntry


class FakeCommit:
    def __init__(self, subject: str, author: str = "dev"):
        self.subject = subject
        self.author = author


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_scope_flag(p)
    return p


# --- add_scope_flag ---

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.scope_report is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--scope-report"])
    assert args.scope_report is True


def test_top_scopes_default():
    args = _make_parser().parse_args([])
    assert args.top_scopes == 10


def test_top_scopes_custom():
    args = _make_parser().parse_args(["--top-scopes", "5"])
    assert args.top_scopes == 5


# --- maybe_render_scope ---

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("feat(api): something")]
    assert maybe_render_scope(args, commits) == ""


def test_returns_output_when_flag_on():
    args = _make_parser().parse_args(["--scope-report"])
    commits = [FakeCommit("feat(api): endpoint")]
    result = maybe_render_scope(args, commits)
    assert "api" in result


def test_empty_commits_with_flag_returns_empty_string():
    args = _make_parser().parse_args(["--scope-report"])
    assert maybe_render_scope(args, []) == ""


def test_respects_top_scopes_limit():
    args = _make_parser().parse_args(["--scope-report", "--top-scopes", "1"])
    commits = [
        FakeCommit("feat(api): a"),
        FakeCommit("feat(api): b"),
        FakeCommit("fix(ui): c"),
    ]
    result = maybe_render_scope(args, commits)
    assert "api" in result
    assert "ui" not in result


# --- scope_summary_line ---

def test_summary_no_entries():
    line = scope_summary_line([])
    assert "No" in line or "no" in line.lower()


def test_summary_shows_top_scope():
    entries = [ScopeEntry(scope="auth", count=5), ScopeEntry(scope="ui", count=2)]
    line = scope_summary_line(entries)
    assert "auth" in line
    assert "5" in line


def test_summary_shows_scope_count():
    entries = [
        ScopeEntry(scope="auth", count=3),
        ScopeEntry(scope="api", count=1),
    ]
    line = scope_summary_line(entries)
    assert "2" in line
