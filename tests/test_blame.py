"""Tests for gitlog_digest.blame."""

from __future__ import annotations

import pytest

from gitlog_digest.blame import (
    FileBlame,
    blame_file,
    blame_files,
    parse_blame_output,
)


# ---------------------------------------------------------------------------
# FileBlame unit tests
# ---------------------------------------------------------------------------

class TestFileBlame:
    def test_top_author_returns_highest(self):
        fb = FileBlame(path="foo.py", line_counts={"Alice": 10, "Bob": 3})
        assert fb.top_author == "Alice"

    def test_top_author_none_when_empty(self):
        fb = FileBlame(path="foo.py")
        assert fb.top_author is None

    def test_total_lines_sums_counts(self):
        fb = FileBlame(path="foo.py", line_counts={"Alice": 7, "Bob": 3})
        assert fb.total_lines == 10

    def test_total_lines_zero_when_empty(self):
        fb = FileBlame(path="foo.py")
        assert fb.total_lines == 0


# ---------------------------------------------------------------------------
# parse_blame_output
# ---------------------------------------------------------------------------

PORCELAIN_SAMPLE = [
    "abc123 1 1 3",
    "author Alice",
    "author-mail <alice@example.com>",
    "summary initial commit",
    "abc123 1 2",
    "author Alice",
    "author-mail <alice@example.com>",
    "abc123 1 3",
    "author Bob",
    "author-mail <bob@example.com>",
]


def test_parse_counts_authors():
    counts = parse_blame_output(PORCELAIN_SAMPLE)
    assert counts["Alice"] == 2
    assert counts["Bob"] == 1


def test_parse_empty_input():
    assert parse_blame_output([]) == {}


def test_parse_ignores_non_author_lines():
    lines = ["summary something", "filename foo.py", "author Carol"]
    counts = parse_blame_output(lines)
    assert list(counts.keys()) == ["Carol"]


# ---------------------------------------------------------------------------
# blame_file / blame_files with monkeypatching
# ---------------------------------------------------------------------------

def test_blame_file_uses_parsed_output(monkeypatch):
    monkeypatch.setattr(
        "gitlog_digest.blame._run_blame",
        lambda repo, fp: PORCELAIN_SAMPLE,
    )
    fb = blame_file("/repo", "foo.py")
    assert fb.path == "foo.py"
    assert fb.top_author == "Alice"


def test_blame_files_skips_empty(monkeypatch):
    def fake_run(repo, fp):
        return [] if fp == "empty.py" else PORCELAIN_SAMPLE

    monkeypatch.setattr("gitlog_digest.blame._run_blame", fake_run)
    results = blame_files("/repo", ["foo.py", "empty.py"])
    assert len(results) == 1
    assert results[0].path == "foo.py"


def test_blame_files_returns_all_valid(monkeypatch):
    monkeypatch.setattr(
        "gitlog_digest.blame._run_blame",
        lambda repo, fp: PORCELAIN_SAMPLE,
    )
    results = blame_files("/repo", ["a.py", "b.py"])
    assert len(results) == 2
