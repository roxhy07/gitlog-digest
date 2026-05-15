"""Tests for gitlog_digest/topic_report.py"""
import pytest
from dataclasses import dataclass, field
from typing import List

from gitlog_digest.topic_report import (
    _extract_prefix,
    build_topic_map,
    format_topic_report,
    TopicBucket,
)


@dataclass
class FakeCommit:
    subject: str
    author: str = "dev"
    files_changed: List[str] = field(default_factory=list)


# --- _extract_prefix ---

def test_feat_prefix():
    assert _extract_prefix("feat: add login") == "feat"

def test_fix_prefix_with_scope():
    assert _extract_prefix("fix(auth): null check") == "fix"

def test_chore_prefix_uppercase():
    assert _extract_prefix("Chore: bump deps") == "chore"

def test_unknown_returns_other():
    assert _extract_prefix("initial commit") == "other"

def test_empty_subject_returns_other():
    assert _extract_prefix("") == "other"

def test_refactor_prefix():
    assert _extract_prefix("refactor: extract helper") == "refactor"

def test_prefix_with_whitespace_after_colon():
    """Prefix should be extracted even when there's extra spacing."""
    assert _extract_prefix("feat:  add something") == "feat"

def test_prefix_no_description_after_colon():
    """A subject with just a prefix and colon but no description."""
    assert _extract_prefix("fix:") == "fix"


# --- build_topic_map ---

def test_empty_commits_returns_empty_map():
    result = build_topic_map([])
    assert result == {}

def test_single_commit_creates_bucket():
    commits = [FakeCommit(subject="feat: new thing")]
    result = build_topic_map(commits)
    assert "feat" in result
    assert result["feat"].count == 1

def test_multiple_commits_same_prefix():
    commits = [
        FakeCommit(subject="fix: bug a"),
        FakeCommit(subject="fix: bug b"),
    ]
    result = build_topic_map(commits)
    assert result["fix"].count == 2

def test_mixed_prefixes_separate_buckets():
    commits = [
        FakeCommit(subject="feat: x"),
        FakeCommit(subject="docs: y"),
        FakeCommit(subject="feat: z"),
    ]
    result = build_topic_map(commits)
    assert result["feat"].count == 2
    assert result["docs"].count == 1

def test_other_bucket_for_unknown():
    commits = [FakeCommit(subject="random message")]
    result = build_topic_map(commits)
    assert "other" in result

def test_bucket_count_matches_total_commits():
    """Sum of all bucket counts should equal the number of commits passed in."""
    commits = [
        FakeCommit(subject="feat: a"),
        FakeCommit(subject="fix: b"),
        FakeCommit(subject="random"),
        FakeCommit(subject="chore: c"),
    ]
    result = build_topic_map(commits)
    total = sum(bucket.count for bucket in result.values())
    assert total == len(commits)


# --- format_topic_report ---

def test_empty_buckets_returns_empty_string():
    assert format_topic_report({}) == ""

def test_output_contains_header():
    commits = [FakeCommit(subject="feat: a")]
    buckets = build_topic_map(commits)
    out = format_topic_report(buckets)
    assert "Commits by Topic" in out

def test_output_contains_label():
    commits = [FakeCommit(subject="chore: tidy")]
    buckets = build_topic_map(commits)
    out = format_topic_report(buckets)
    assert "chore" in out

def test_top_n_limits_rows():
    subjects = [
        "feat: a", "fix: b", "chore: c", "docs: d",
        "style: e", "refactor: f", "perf: g",
    ]
    commits = [FakeCommit(subject=s) for s in subjects]
    buckets = build_topic_map(commits)
    out = format_topic_report(buckets, top_n=3)
    # Each label appears once; only 3 should be present
    found = [label for label in ["feat", "fix", "chore", "docs", "style", "refactor", "perf"] if label in out]
    assert len(found) == 3
