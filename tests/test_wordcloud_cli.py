"""Tests for gitlog_digest.wordcloud_cli."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import pytest

from gitlog_digest.wordcloud_cli import (
    add_wordcloud_flag,
    maybe_render_wordcloud,
    wordcloud_summary_line,
)


@dataclass
class FakeCommit:
    subject: str = ""


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_wordcloud_flag(p)
    return p


# ---------------------------------------------------------------------------
# add_wordcloud_flag
# ---------------------------------------------------------------------------

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.wordcloud is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--wordcloud"])
    assert args.wordcloud is True


def test_top_n_default():
    args = _make_parser().parse_args([])
    assert args.wordcloud_top_n == 10


def test_top_n_custom():
    args = _make_parser().parse_args(["--wordcloud-top-n", "5"])
    assert args.wordcloud_top_n == 5


# ---------------------------------------------------------------------------
# maybe_render_wordcloud
# ---------------------------------------------------------------------------

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("add feature"), FakeCommit("fix bug")]
    assert maybe_render_wordcloud(args, commits) == ""


def test_returns_section_when_flag_on():
    args = _make_parser().parse_args(["--wordcloud"])
    commits = [FakeCommit("refactor login module"), FakeCommit("refactor logout")]
    result = maybe_render_wordcloud(args, commits)
    assert "refactor" in result


def test_respects_top_n_argument():
    args = _make_parser().parse_args(["--wordcloud", "--wordcloud-top-n", "1"])
    commits = [
        FakeCommit("add login feature"),
        FakeCommit("add logout feature"),
        FakeCommit("fix redirect"),
    ]
    result = maybe_render_wordcloud(args, commits)
    # Only 1 word row should appear; 'add' and 'feature' tie at 2 each
    lines = [l for l in result.splitlines() if "█" in l]
    assert len(lines) == 1


def test_empty_commits_returns_empty_section():
    args = _make_parser().parse_args(["--wordcloud"])
    assert maybe_render_wordcloud(args, []) == ""


# ---------------------------------------------------------------------------
# wordcloud_summary_line
# ---------------------------------------------------------------------------

def test_summary_line_empty_commits():
    assert wordcloud_summary_line([]) == ""


def test_summary_line_contains_top_word():
    commits = [FakeCommit("refactor refactor add")]
    line = wordcloud_summary_line(commits)
    assert "refactor" in line
    assert line.startswith("Top words:")


def test_summary_line_respects_n():
    commits = [
        FakeCommit("alpha beta gamma delta epsilon zeta"),
    ]
    line = wordcloud_summary_line(commits, n=2)
    words = line.replace("Top words: ", "").split(", ")
    assert len(words) == 2
