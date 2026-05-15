"""Tests for gitlog_digest.label_cli."""

from __future__ import annotations

import argparse
import pytest
from gitlog_digest.label_cli import (
    add_label_flag,
    label_summary_line,
    maybe_render_labels,
)
from gitlog_digest.label_report import LabelEntry


class FakeCommit:
    def __init__(self, subject: str, author: str = "Dev"):
        self.subject = subject
        self.author = author


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_label_flag(p)
    return p


# --- add_label_flag ---

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.labels is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--labels"])
    assert args.labels is True


def test_top_labels_default():
    args = _make_parser().parse_args([])
    assert args.top_labels == 10


def test_top_labels_custom():
    args = _make_parser().parse_args(["--top-labels", "5"])
    assert args.top_labels == 5


# --- maybe_render_labels ---

def test_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("Fix PROJ-1")]
    assert maybe_render_labels(args, commits) == ""


def test_returns_section_when_flag_on():
    args = _make_parser().parse_args(["--labels"])
    commits = [FakeCommit("Fix PROJ-1")]
    result = maybe_render_labels(args, commits)
    assert "PROJ-1" in result


def test_empty_commits_returns_empty_string():
    args = _make_parser().parse_args(["--labels"])
    result = maybe_render_labels(args, [])
    assert result == ""


def test_respects_top_n():
    args = _make_parser().parse_args(["--labels", "--top-labels", "1"])
    commits = [
        FakeCommit("PROJ-1 a"), FakeCommit("PROJ-1 b"), FakeCommit("PROJ-2 c"),
    ]
    result = maybe_render_labels(args, commits)
    assert "PROJ-1" in result
    assert "PROJ-2" not in result


# --- label_summary_line ---

def test_summary_no_labels():
    assert label_summary_line({}) == "No ticket labels referenced."


def test_summary_single_label():
    m = {"PROJ-1": LabelEntry(label="PROJ-1", commit_count=3)}
    line = label_summary_line(m)
    assert "1 unique label" in line
    assert "3 commit" in line


def test_summary_multiple_labels():
    m = {
        "PROJ-1": LabelEntry(label="PROJ-1", commit_count=2),
        "PROJ-2": LabelEntry(label="PROJ-2", commit_count=1),
    }
    line = label_summary_line(m)
    assert "2 unique label" in line
    assert "3 commit" in line
