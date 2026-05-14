"""Tests for gitlog_digest.coauthor_report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.coauthor_report import (
    _extract_coauthors,
    build_coauthor_map,
    top_pairs,
    format_coauthor_section,
    CoAuthorPair,
)


@dataclass
class FakeCommit:
    author: str
    body: str = ""


# ---------------------------------------------------------------------------
# _extract_coauthors
# ---------------------------------------------------------------------------

def test_extract_single_coauthor():
    body = "Co-authored-by: Alice <alice@example.com>"
    assert _extract_coauthors(body) == ["Alice"]


def test_extract_multiple_coauthors():
    body = (
        "Some message\n"
        "Co-authored-by: Alice <alice@example.com>\n"
        "Co-authored-by: Bob <bob@example.com>"
    )
    result = _extract_coauthors(body)
    assert result == ["Alice", "Bob"]


def test_extract_case_insensitive_trailer():
    body = "CO-AUTHORED-BY: Charlie <charlie@example.com>"
    assert _extract_coauthors(body) == ["Charlie"]


def test_extract_empty_body_returns_empty():
    assert _extract_coauthors("") == []


def test_extract_no_trailer_returns_empty():
    body = "Fix typo in README"
    assert _extract_coauthors(body) == []


# ---------------------------------------------------------------------------
# build_coauthor_map
# ---------------------------------------------------------------------------

def test_single_pair_counted():
    commits = [
        FakeCommit(author="Dave", body="Co-authored-by: Eve <eve@example.com>"),
    ]
    result = build_coauthor_map(commits)
    assert result == {("Dave", "Eve"): 1}


def test_pair_accumulated_across_commits():
    commits = [
        FakeCommit(author="Dave", body="Co-authored-by: Eve <eve@example.com>"),
        FakeCommit(author="Dave", body="Co-authored-by: Eve <eve@example.com>"),
    ]
    result = build_coauthor_map(commits)
    assert result[("Dave", "Eve")] == 2


def test_commit_without_body_skipped():
    commits = [FakeCommit(author="Frank", body="")]
    result = build_coauthor_map(commits)
    assert result == {}


def test_none_body_handled():
    commits = [FakeCommit(author="Grace", body=None)]
    result = build_coauthor_map(commits)
    assert result == {}


# ---------------------------------------------------------------------------
# top_pairs
# ---------------------------------------------------------------------------

def test_top_pairs_sorted_descending():
    pair_map = {("A", "B"): 5, ("C", "D"): 10, ("E", "F"): 1}
    result = top_pairs(pair_map, n=3)
    assert result[0].commit_count == 10
    assert result[1].commit_count == 5
    assert result[2].commit_count == 1


def test_top_pairs_respects_n():
    pair_map = {("A", "B"): 3, ("C", "D"): 7, ("E", "F"): 2}
    result = top_pairs(pair_map, n=2)
    assert len(result) == 2


def test_top_pairs_empty_map():
    assert top_pairs({}) == []


# ---------------------------------------------------------------------------
# format_coauthor_section
# ---------------------------------------------------------------------------

def test_format_empty_pairs_returns_empty():
    assert format_coauthor_section([]) == ""


def test_format_contains_pair_names():
    pairs = [CoAuthorPair(driver="Alice", navigator="Bob", commit_count=3)]
    output = format_coauthor_section(pairs)
    assert "Alice" in output
    assert "Bob" in output
    assert "3" in output


def test_format_contains_header():
    pairs = [CoAuthorPair(driver="X", navigator="Y", commit_count=1)]
    output = format_coauthor_section(pairs)
    assert "Co-author Pairs" in output
