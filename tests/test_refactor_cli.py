"""Tests for gitlog_digest.refactor_cli."""

from __future__ import annotations

import argparse

import pytest
from gitlog_digest.refactor_cli import (
    add_refactor_flag,
    maybe_render_refactor,
    refactor_summary_line,
)


class FakeCommit:
    def __init__(self, author: str, subject: str):
        self.author = author
        self.subject = subject


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    add_refactor_flag(parser)
    return parser


# --- add_refactor_flag ---

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.refactor is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--refactor"])
    assert args.refactor is True


def test_top_refactorers_default():
    args = _make_parser().parse_args([])
    assert args.top_refactorers == 5


def test_top_refactorers_custom():
    args = _make_parser().parse_args(["--top-refactorers", "3"])
    assert args.top_refactorers == 3


# --- maybe_render_refactor ---

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("alice", "refactor: something")]
    assert maybe_render_refactor(args, commits) == ""


def test_returns_content_when_flag_on():
    args = _make_parser().parse_args(["--refactor"])
    commits = [FakeCommit("alice", "refactor: something")]
    result = maybe_render_refactor(args, commits)
    assert "alice" in result


def test_returns_empty_string_for_no_refactor_commits():
    args = _make_parser().parse_args(["--refactor"])
    commits = [FakeCommit("alice", "add new feature")]
    result = maybe_render_refactor(args, commits)
    assert result == ""


def test_respects_top_n_arg():
    args = _make_parser().parse_args(["--refactor", "--top-refactorers", "1"])
    commits = [
        FakeCommit("alice", "refactor A"),
        FakeCommit("alice", "refactor B"),
        FakeCommit("bob", "refactor C"),
    ]
    result = maybe_render_refactor(args, commits)
    assert "alice" in result
    assert "bob" not in result


# --- refactor_summary_line ---

def test_summary_line_no_refactors():
    result = refactor_summary_line([FakeCommit("alice", "add feature")])
    assert result == "No refactor commits detected."


def test_summary_line_counts_commits():
    commits = [
        FakeCommit("alice", "refactor: split module"),
        FakeCommit("bob", "cleanup old code"),
    ]
    result = refactor_summary_line(commits)
    assert "2" in result
    assert "2" in result  # 2 authors


def test_summary_line_single_author():
    commits = [FakeCommit("alice", "refactor: tidy utils")]
    result = refactor_summary_line(commits)
    assert "1" in result
