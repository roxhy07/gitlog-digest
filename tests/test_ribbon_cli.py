"""Tests for gitlog_digest.ribbon_cli."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.ribbon_cli import (
    add_ribbon_flag,
    maybe_render_ribbons,
    ribbon_summary_line,
)


@dataclass
class FakeCommit:
    author: str
    files_changed: List[str] = field(default_factory=list)


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_ribbon_flag(p)
    return p


def _parse(args=None):
    return _make_parser().parse_args(args or [])


# --- add_ribbon_flag ---

def test_flag_default_false():
    args = _parse([])
    assert args.ribbons is False


def test_flag_enabled():
    args = _parse(["--ribbons"])
    assert args.ribbons is True


def test_top_ribbons_default():
    args = _parse([])
    assert args.top_ribbons == 10


def test_top_ribbons_custom():
    args = _parse(["--top-ribbons", "5"])
    assert args.top_ribbons == 5


# --- maybe_render_ribbons ---

def test_returns_empty_when_flag_not_set():
    args = _parse([])
    commits = [FakeCommit(author="alice")]
    result = maybe_render_ribbons(args, commits)
    assert result == ""


def test_returns_non_empty_when_flag_set():
    args = _parse(["--ribbons"])
    commits = [FakeCommit(author="alice")]
    result = maybe_render_ribbons(args, commits)
    assert len(result) > 0


def test_returns_empty_string_for_empty_commits_with_flag():
    args = _parse(["--ribbons"])
    result = maybe_render_ribbons(args, [])
    assert result == ""


def test_top_n_respected_in_render():
    args = _parse(["--ribbons", "--top-ribbons", "2"])
    commits = [FakeCommit(author=f"author{i}") for i in range(10)]
    result = maybe_render_ribbons(args, commits)
    author_lines = [l for l in result.splitlines() if l.startswith("-")]
    assert len(author_lines) == 2


# --- ribbon_summary_line ---

def test_summary_line_empty_commits():
    assert ribbon_summary_line([]) == ""


def test_summary_line_contains_contributor_count():
    commits = [FakeCommit(author="alice"), FakeCommit(author="bob")]
    line = ribbon_summary_line(commits)
    assert "2" in line


def test_summary_line_contains_badge_word():
    commits = [FakeCommit(author="alice")]
    line = ribbon_summary_line(commits)
    assert "badge" in line.lower()
