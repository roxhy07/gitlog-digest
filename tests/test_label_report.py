"""Tests for gitlog_digest.label_report."""

from __future__ import annotations

import pytest
from gitlog_digest.label_report import (
    LabelEntry,
    _extract_labels,
    build_label_map,
    format_label_section,
    top_n_labels,
)


class FakeCommit:
    def __init__(self, subject: str, author: str = "Alice"):
        self.subject = subject
        self.author = author


# --- _extract_labels ---

def test_extract_single_label():
    assert _extract_labels("Fix PROJ-123 crash") == ["PROJ-123"]


def test_extract_multiple_labels():
    result = _extract_labels("Refs JIRA-1 and JIRA-2")
    assert result == ["JIRA-1", "JIRA-2"]


def test_extract_no_label():
    assert _extract_labels("chore: update deps") == []


def test_extract_lowercase_not_matched():
    assert _extract_labels("fix jira-10 issue") == []


def test_extract_gh_style():
    assert _extract_labels("Close GH-42") == ["GH-42"]


# --- build_label_map ---

def test_empty_commits_returns_empty_map():
    assert build_label_map([]) == {}


def test_single_label_counted():
    commits = [FakeCommit("Fix PROJ-1 bug")]
    m = build_label_map(commits)
    assert "PROJ-1" in m
    assert m["PROJ-1"].commit_count == 1


def test_same_label_across_commits_accumulates():
    commits = [
        FakeCommit("PROJ-1 part one", author="Alice"),
        FakeCommit("PROJ-1 part two", author="Bob"),
    ]
    m = build_label_map(commits)
    assert m["PROJ-1"].commit_count == 2
    assert sorted(m["PROJ-1"].authors) == ["Alice", "Bob"]


def test_authors_deduplicated():
    commits = [
        FakeCommit("PROJ-1 fix", author="Alice"),
        FakeCommit("PROJ-1 followup", author="Alice"),
    ]
    m = build_label_map(commits)
    assert m["PROJ-1"].authors == ["Alice"]


def test_multiple_labels_in_one_commit():
    commits = [FakeCommit("Refs JIRA-10 and JIRA-20")]
    m = build_label_map(commits)
    assert "JIRA-10" in m
    assert "JIRA-20" in m


# --- top_n_labels ---

def test_top_n_returns_descending_order():
    commits = [
        FakeCommit("PROJ-1 a"), FakeCommit("PROJ-1 b"), FakeCommit("PROJ-2 c"),
    ]
    m = build_label_map(commits)
    top = top_n_labels(m, n=2)
    assert top[0].label == "PROJ-1"
    assert top[1].label == "PROJ-2"


def test_top_n_respects_limit():
    commits = [FakeCommit(f"PROJ-{i} msg") for i in range(20)]
    m = build_label_map(commits)
    assert len(top_n_labels(m, n=5)) == 5


# --- format_label_section ---

def test_format_empty_returns_empty_string():
    assert format_label_section({}) == ""


def test_format_contains_label():
    commits = [FakeCommit("Fix PROJ-99 crash")]
    m = build_label_map(commits)
    output = format_label_section(m)
    assert "PROJ-99" in output


def test_format_contains_header():
    commits = [FakeCommit("Fix PROJ-1")]
    m = build_label_map(commits)
    output = format_label_section(m)
    assert "Ticket Labels" in output


def test_format_shows_author():
    commits = [FakeCommit("PROJ-5 work", author="Carol")]
    m = build_label_map(commits)
    output = format_label_section(m)
    assert "Carol" in output
