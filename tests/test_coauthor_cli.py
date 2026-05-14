"""Tests for gitlog_digest.coauthor_cli."""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import pytest

from gitlog_digest.coauthor_cli import (
    add_coauthor_flag,
    maybe_render_coauthors,
    coauthor_summary_line,
)
from gitlog_digest.coauthor_report import CoAuthorPair


@dataclass
class FakeCommit:
    author: str
    body: str = ""


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_coauthor_flag(p)
    return p


# ---------------------------------------------------------------------------
# add_coauthor_flag
# ---------------------------------------------------------------------------

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.coauthors is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--coauthors"])
    assert args.coauthors is True


def test_top_n_default():
    args = _make_parser().parse_args([])
    assert args.coauthors_top_n == 10


def test_top_n_custom():
    args = _make_parser().parse_args(["--coauthors-top-n", "5"])
    assert args.coauthors_top_n == 5


# ---------------------------------------------------------------------------
# maybe_render_coauthors
# ---------------------------------------------------------------------------

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit(author="Alice", body="Co-authored-by: Bob <b@x.com>")]
    result = maybe_render_coauthors(args, commits)
    assert result == ""


def test_returns_section_when_flag_on():
    args = _make_parser().parse_args(["--coauthors"])
    commits = [FakeCommit(author="Alice", body="Co-authored-by: Bob <b@x.com>")]
    result = maybe_render_coauthors(args, commits)
    assert "Alice" in result
    assert "Bob" in result


def test_empty_commits_returns_empty_section():
    args = _make_parser().parse_args(["--coauthors"])
    result = maybe_render_coauthors(args, [])
    assert result == ""


def test_top_n_limits_output():
    args = _make_parser().parse_args(["--coauthors", "--coauthors-top-n", "1"])
    commits = [
        FakeCommit(author="A", body="Co-authored-by: B <b@x.com>"),
        FakeCommit(author="C", body="Co-authored-by: D <d@x.com>"),
    ]
    result = maybe_render_coauthors(args, commits)
    # Only one pair should appear — count lines with "+"
    pair_lines = [ln for ln in result.splitlines() if "+" in ln]
    assert len(pair_lines) == 1


# ---------------------------------------------------------------------------
# coauthor_summary_line
# ---------------------------------------------------------------------------

def test_summary_line_no_pairs():
    line = coauthor_summary_line([])
    assert "No co-author" in line


def test_summary_line_shows_top_pair():
    pairs = [CoAuthorPair(driver="Alice", navigator="Bob", commit_count=7)]
    line = coauthor_summary_line(pairs)
    assert "Alice" in line
    assert "Bob" in line
    assert "7" in line
