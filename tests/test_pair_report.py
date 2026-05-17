"""Tests for gitlog_digest.pair_report."""
from __future__ import annotations

import argparse
from types import SimpleNamespace

import pytest

from gitlog_digest.pair_report import (
    PairEntry,
    _pair_key,
    build_pair_map,
    format_pair_section,
    top_pairs,
)
from gitlog_digest.pair_cli import add_pair_flag, maybe_render_pairs, pair_summary_line


class FakeCommit:
    def __init__(self, author: str, hash_: str, files=None):
        self.author = author
        self.hash = hash_
        self.files_changed = files or []


# ---------------------------------------------------------------------------
# _pair_key
# ---------------------------------------------------------------------------

def test_pair_key_sorts_alphabetically():
    assert _pair_key("Bob", "Alice") == ("Alice", "Bob")


def test_pair_key_already_sorted():
    assert _pair_key("Alice", "Bob") == ("Alice", "Bob")


# ---------------------------------------------------------------------------
# build_pair_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty():
    assert build_pair_map([]) == {}


def test_no_shared_files_returns_empty():
    commits = [
        FakeCommit("Alice", "a1", ["foo.py"]),
        FakeCommit("Bob", "b1", ["bar.py"]),
    ]
    assert build_pair_map(commits) == {}


def test_shared_file_creates_pair():
    commits = [
        FakeCommit("Alice", "a1", ["shared.py"]),
        FakeCommit("Bob", "b1", ["shared.py"]),
    ]
    pair_map = build_pair_map(commits)
    assert len(pair_map) == 1
    key = ("Alice", "Bob")
    assert key in pair_map
    assert pair_map[key].shared_files == 1


def test_multiple_shared_files_counted():
    commits = [
        FakeCommit("Alice", "a1", ["a.py", "b.py"]),
        FakeCommit("Bob", "b1", ["a.py", "b.py"]),
    ]
    pair_map = build_pair_map(commits)
    key = ("Alice", "Bob")
    assert pair_map[key].shared_files == 2


def test_commit_overlap_counted():
    commits = [
        FakeCommit("Alice", "x1", ["f.py"]),
        FakeCommit("Bob", "x1", ["f.py"]),  # same hash => overlap
    ]
    pair_map = build_pair_map(commits)
    key = ("Alice", "Bob")
    assert pair_map[key].commit_overlap == 1


# ---------------------------------------------------------------------------
# top_pairs
# ---------------------------------------------------------------------------

def test_top_pairs_limits_results():
    entries = {(str(i), str(i + 1)): PairEntry(str(i), str(i + 1), i, 0) for i in range(10)}
    result = top_pairs(entries, n=3)
    assert len(result) == 3


def test_top_pairs_sorted_by_shared_files():
    commits = [
        FakeCommit("Alice", "a1", ["x.py", "y.py", "z.py"]),
        FakeCommit("Bob", "b1", ["x.py", "y.py", "z.py"]),
        FakeCommit("Carol", "c1", ["x.py"]),
        FakeCommit("Alice", "a2", ["x.py"]),  # Alice already counted for x.py
    ]
    pair_map = build_pair_map(commits)
    ranked = top_pairs(pair_map)
    assert ranked[0].shared_files >= ranked[-1].shared_files


# ---------------------------------------------------------------------------
# format_pair_section
# ---------------------------------------------------------------------------

def test_format_empty_returns_empty_string():
    assert format_pair_section([]) == ""


def test_format_contains_author_names():
    entries = [PairEntry("Alice", "Bob", shared_files=3, commit_overlap=1)]
    out = format_pair_section(entries)
    assert "Alice" in out
    assert "Bob" in out


def test_format_contains_shared_file_count():
    entries = [PairEntry("Alice", "Bob", shared_files=7, commit_overlap=2)]
    out = format_pair_section(entries)
    assert "7" in out


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_parser():
    p = argparse.ArgumentParser()
    add_pair_flag(p)
    return p


def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.pairs is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--pairs"])
    assert args.pairs is True


def test_top_pairs_default():
    args = _make_parser().parse_args([])
    assert args.top_pairs == 5


def test_maybe_render_disabled_returns_empty():
    args = SimpleNamespace(pairs=False, top_pairs=5)
    assert maybe_render_pairs(args, []) == ""


def test_maybe_render_enabled_returns_string():
    commits = [
        FakeCommit("Alice", "a1", ["f.py"]),
        FakeCommit("Bob", "b1", ["f.py"]),
    ]
    args = SimpleNamespace(pairs=True, top_pairs=5)
    result = maybe_render_pairs(args, commits)
    assert isinstance(result, str)


def test_pair_summary_line_disabled():
    args = SimpleNamespace(pairs=False)
    assert pair_summary_line(args, []) == ""


def test_pair_summary_line_enabled():
    commits = [
        FakeCommit("Alice", "a1", ["f.py"]),
        FakeCommit("Bob", "b1", ["f.py"]),
    ]
    args = SimpleNamespace(pairs=True)
    line = pair_summary_line(args, commits)
    assert "pair" in line
