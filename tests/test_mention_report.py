"""Tests for gitlog_digest.mention_report."""

from __future__ import annotations

import pytest
from gitlog_digest.mention_report import (
    MentionEntry,
    _extract_mentions,
    _mention_bar,
    build_mention_map,
    format_mention_section,
    top_n_mentions,
)


class FakeCommit:
    def __init__(self, hash: str, subject: str = "", body: str = ""):
        self.hash = hash
        self.subject = subject
        self.body = body


# --- _extract_mentions ---

def test_extract_single_mention():
    assert _extract_mentions("thanks @alice!") == ["alice"]


def test_extract_multiple_mentions():
    result = _extract_mentions("cc @Alice and @Bob")
    assert result == ["alice", "bob"]


def test_extract_lowercases():
    assert _extract_mentions("@UPPER") == ["upper"]


def test_extract_no_mentions():
    assert _extract_mentions("no mentions here") == []


def test_extract_mention_with_dots_and_dashes():
    assert _extract_mentions("ping @john.doe-dev") == ["john.doe-dev"]


# --- build_mention_map ---

def test_empty_commits_returns_empty_map():
    assert build_mention_map([]) == {}


def test_single_mention_counted():
    commits = [FakeCommit("abc", subject="fix bug, cc @alice")]
    result = build_mention_map(commits)
    assert "alice" in result
    assert result["alice"].count == 1


def test_same_mention_in_two_commits_counts_twice():
    commits = [
        FakeCommit("a1", subject="cc @bob"),
        FakeCommit("a2", subject="also @bob"),
    ]
    result = build_mention_map(commits)
    assert result["bob"].count == 2


def test_duplicate_mention_within_same_commit_counted_once():
    commits = [FakeCommit("x1", subject="@carol and @carol again")]
    result = build_mention_map(commits)
    assert result["carol"].count == 1


def test_mention_in_body_captured():
    commits = [FakeCommit("b1", subject="update", body="reviewed by @dave")]
    result = build_mention_map(commits)
    assert "dave" in result


def test_commit_hashes_appended():
    commits = [
        FakeCommit("h1", subject="@eve"),
        FakeCommit("h2", subject="@eve again"),
    ]
    result = build_mention_map(commits)
    assert "h1" in result["eve"].commit_hashes
    assert "h2" in result["eve"].commit_hashes


# --- top_n_mentions ---

def test_top_n_returns_sorted_by_count():
    mention_map = {
        "alice": MentionEntry("alice", count=5),
        "bob": MentionEntry("bob", count=10),
        "carol": MentionEntry("carol", count=1),
    }
    top = top_n_mentions(mention_map, n=2)
    assert [e.handle for e in top] == ["bob", "alice"]


def test_top_n_respects_limit():
    mention_map = {f"user{i}": MentionEntry(f"user{i}", count=i) for i in range(20)}
    assert len(top_n_mentions(mention_map, n=5)) == 5


# --- _mention_bar ---

def test_full_bar_when_equal():
    assert _mention_bar(10, 10, 10) == "#" * 10


def test_empty_bar_when_zero_max():
    assert _mention_bar(0, 0, 10) == " " * 10


# --- format_mention_section ---

def test_format_empty_returns_empty_string():
    assert format_mention_section([]) == ""


def test_format_contains_handle():
    entries = [MentionEntry("alice", count=3)]
    output = format_mention_section(entries)
    assert "@alice" in output


def test_format_contains_count():
    entries = [MentionEntry("bob", count=7)]
    output = format_mention_section(entries)
    assert "7" in output
