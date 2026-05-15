"""Tests for gitlog_digest/branch_cli.py"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import List
from unittest.mock import patch

from gitlog_digest.branch_cli import (
    add_branch_flag,
    branch_summary_line,
    maybe_render_branch,
)
from gitlog_digest.branch_report import BranchEntry


@dataclass
class FakeCommit:
    hash: str
    author: str
    files_changed: List[str] = field(default_factory=list)


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_branch_flag(p)
    return p


# ---------------------------------------------------------------------------
# add_branch_flag
# ---------------------------------------------------------------------------

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.branch_report is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--branch-report"])
    assert args.branch_report is True


def test_top_branches_default():
    args = _make_parser().parse_args([])
    assert args.top_branches == 10


def test_top_branches_custom():
    args = _make_parser().parse_args(["--top-branches", "5"])
    assert args.top_branches == 5


# ---------------------------------------------------------------------------
# maybe_render_branch
# ---------------------------------------------------------------------------

def test_maybe_render_branch_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    result = maybe_render_branch(args, [], repo=".")
    assert result == ""


def test_maybe_render_branch_calls_build_and_format():
    args = _make_parser().parse_args(["--branch-report", "--top-branches", "3"])
    commits = [FakeCommit(hash="abc", author="Alice")]
    fake_entries = [BranchEntry("main", 1, ["Alice"])]

    with patch(
        "gitlog_digest.branch_cli.build_branch_map", return_value={"main": fake_entries[0]}
    ), patch(
        "gitlog_digest.branch_cli.top_n_branches", return_value=fake_entries
    ), patch(
        "gitlog_digest.branch_cli.format_branch_section", return_value="Branch Activity\n---"
    ) as mock_fmt:
        result = maybe_render_branch(args, commits, repo=".")

    mock_fmt.assert_called_once_with(fake_entries)
    assert "Branch Activity" in result


# ---------------------------------------------------------------------------
# branch_summary_line
# ---------------------------------------------------------------------------

def test_branch_summary_line_empty():
    assert branch_summary_line([]) == ""


def test_branch_summary_line_counts():
    entries = [
        BranchEntry("main", 5),
        BranchEntry("dev", 3),
    ]
    line = branch_summary_line(entries)
    assert "2 branch" in line
    assert "8 commits" in line


def test_branch_summary_line_single_branch():
    entries = [BranchEntry("main", 10)]
    line = branch_summary_line(entries)
    assert "1 branch" in line
    assert "10 commits" in line
