"""Tests for gitlog_digest/topic_cli.py"""
import argparse
from dataclasses import dataclass, field
from typing import List

from gitlog_digest.topic_cli import add_topic_flag, maybe_render_topic, topic_summary_line


@dataclass
class FakeCommit:
    subject: str
    author: str = "dev"
    files_changed: List[str] = field(default_factory=list)


def _make_parser():
    parser = argparse.ArgumentParser()
    add_topic_flag(parser)
    return parser


# --- add_topic_flag ---

def test_flag_default_false():
    parser = _make_parser()
    args = parser.parse_args([])
    assert args.topic_breakdown is False

def test_flag_enabled():
    parser = _make_parser()
    args = parser.parse_args(["--topic-breakdown"])
    assert args.topic_breakdown is True

def test_top_n_default():
    parser = _make_parser()
    args = parser.parse_args([])
    assert args.topic_top_n == 10

def test_top_n_custom():
    parser = _make_parser()
    args = parser.parse_args(["--topic-top-n", "5"])
    assert args.topic_top_n == 5


# --- maybe_render_topic ---

def test_returns_empty_when_flag_off():
    parser = _make_parser()
    args = parser.parse_args([])
    commits = [FakeCommit(subject="feat: x")]
    assert maybe_render_topic(args, commits) == ""

def test_returns_section_when_flag_on():
    parser = _make_parser()
    args = parser.parse_args(["--topic-breakdown"])
    commits = [FakeCommit(subject="feat: x"), FakeCommit(subject="fix: y")]
    result = maybe_render_topic(args, commits)
    assert "Commits by Topic" in result

def test_respects_top_n():
    parser = _make_parser()
    args = parser.parse_args(["--topic-breakdown", "--topic-top-n", "1"])
    commits = [
        FakeCommit(subject="feat: a"),
        FakeCommit(subject="fix: b"),
        FakeCommit(subject="chore: c"),
    ]
    result = maybe_render_topic(args, commits)
    # Only the top 1 topic should appear; others should not
    present = [t for t in ["feat", "fix", "chore"] if t in result]
    assert len(present) == 1


# --- topic_summary_line ---

def test_none_for_empty_commits():
    assert topic_summary_line([]) is None

def test_summary_line_contains_topics():
    commits = [
        FakeCommit(subject="feat: a"),
        FakeCommit(subject="feat: b"),
        FakeCommit(subject="fix: c"),
    ]
    line = topic_summary_line(commits)
    assert line is not None
    assert "feat" in line
    assert "fix" in line

def test_summary_line_starts_with_label():
    commits = [FakeCommit(subject="docs: readme")]
    line = topic_summary_line(commits)
    assert line.startswith("Topics")
