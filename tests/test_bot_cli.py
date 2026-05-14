"""Tests for gitlog_digest.bot_cli."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.bot_cli import (
    add_bot_flag,
    bot_summary_line,
    maybe_render_bots,
)


@dataclass
class FakeCommit:
    author: str
    subject: str
    files_changed: List[str] = field(default_factory=list)


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_bot_flag(p)
    return p


# ---------------------------------------------------------------------------
# add_bot_flag
# ---------------------------------------------------------------------------

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.bots is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--bots"])
    assert args.bots is True


def test_top_bots_default():
    args = _make_parser().parse_args([])
    assert args.top_bots == 5


def test_top_bots_custom():
    args = _make_parser().parse_args(["--top-bots", "3"])
    assert args.top_bots == 3


# ---------------------------------------------------------------------------
# maybe_render_bots
# ---------------------------------------------------------------------------

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit(author="dependabot[bot]", subject="bump x")]
    assert maybe_render_bots(args, commits) == ""


def test_returns_section_when_flag_on():
    args = _make_parser().parse_args(["--bots"])
    commits = [FakeCommit(author="dependabot[bot]", subject="bump requests")]
    result = maybe_render_bots(args, commits)
    assert "dependabot[bot]" in result


def test_returns_empty_when_no_bots_present():
    args = _make_parser().parse_args(["--bots"])
    commits = [FakeCommit(author="Alice", subject="fix bug")]
    assert maybe_render_bots(args, commits) == ""


def test_respects_top_bots_limit(monkeypatch):
    args = _make_parser().parse_args(["--bots", "--top-bots", "1"])
    commits = [
        FakeCommit(author="renovate-bot", subject="update A"),
        FakeCommit(author="renovate-bot", subject="update B"),
        FakeCommit(author="dependabot[bot]", subject="bump X"),
    ]
    result = maybe_render_bots(args, commits)
    # renovate-bot has 2 commits so should appear; dependabot only 1 and limit is 1
    assert "renovate-bot" in result
    assert "dependabot[bot]" not in result


# ---------------------------------------------------------------------------
# bot_summary_line
# ---------------------------------------------------------------------------

def test_summary_empty_when_no_bots():
    commits = [FakeCommit(author="Alice", subject="init")]
    assert bot_summary_line(commits) == ""


def test_summary_shows_total_and_account_count():
    commits = [
        FakeCommit(author="dependabot[bot]", subject="bump x"),
        FakeCommit(author="dependabot[bot]", subject="bump y"),
        FakeCommit(author="renovate-bot", subject="update z"),
    ]
    line = bot_summary_line(commits)
    assert "3 automated commit" in line
    assert "2 bot account" in line


def test_summary_singular_form():
    commits = [FakeCommit(author="renovate-bot", subject="update dep")]
    line = bot_summary_line(commits)
    assert "1 automated commit" in line
    assert "s" not in line.split("automated commit")[1].split(" ")[0]
