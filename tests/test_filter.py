"""Tests for gitlog_digest.filter."""

from datetime import date

import pytest

from gitlog_digest.git_parser import Commit
from gitlog_digest.config import DigestConfig
from gitlog_digest.filter import filter_commits, truncate_subjects, apply_filters


def make_commit(
    author: str = "Alice",
    subject: str = "fix: something",
    hash: str = "abc1234",
    files_changed: list[str] | None = None,
) -> Commit:
    return Commit(
        hash=hash,
        author=author,
        date=date(2024, 1, 15),
        subject=subject,
        files_changed=files_changed or [],
    )


class TestFilterCommits:
    def test_passes_all_by_default(self):
        commits = [make_commit(), make_commit(author="Bob")]
        cfg = DigestConfig()
        assert filter_commits(commits, cfg) == commits

    def test_excludes_author_case_insensitive(self):
        commits = [make_commit(author="Bot"), make_commit(author="Alice")]
        cfg = DigestConfig(exclude_authors=["bot"])
        result = filter_commits(commits, cfg)
        assert len(result) == 1
        assert result[0].author == "Alice"

    def test_excludes_multiple_authors(self):
        commits = [
            make_commit(author="ci"),
            make_commit(author="Alice"),
            make_commit(author="bot"),
        ]
        cfg = DigestConfig(exclude_authors=["ci", "bot"])
        result = filter_commits(commits, cfg)
        assert len(result) == 1

    def test_excludes_by_pattern(self):
        commits = [
            make_commit(subject="chore: update deps"),
            make_commit(subject="fix: real work"),
            make_commit(subject="Merge branch main"),
        ]
        cfg = DigestConfig(exclude_patterns=["chore:*", "Merge *"])
        result = filter_commits(commits, cfg)
        assert len(result) == 1
        assert result[0].subject == "fix: real work"

    def test_empty_commits_returns_empty(self):
        cfg = DigestConfig(exclude_authors=["bot"])
        assert filter_commits([], cfg) == []


class TestTruncateSubjects:
    def test_short_subject_unchanged(self):
        c = make_commit(subject="short")
        result = truncate_subjects([c], max_length=72)
        assert result[0].subject == "short"

    def test_long_subject_truncated(self):
        long_subject = "x" * 80
        c = make_commit(subject=long_subject)
        result = truncate_subjects([c], max_length=72)
        assert len(result[0].subject) == 72
        assert result[0].subject.endswith("…")

    def test_other_fields_preserved(self):
        c = make_commit(author="Alice", subject="x" * 80)
        result = truncate_subjects([c], max_length=10)
        assert result[0].author == "Alice"
        assert result[0].hash == c.hash


class TestApplyFilters:
    def test_combines_filter_and_truncate(self):
        commits = [
            make_commit(author="bot", subject="y" * 80),
            make_commit(author="Alice", subject="z" * 80),
        ]
        cfg = DigestConfig(exclude_authors=["bot"], max_subject_length=20)
        result = apply_filters(commits, cfg)
        assert len(result) == 1
        assert result[0].author == "Alice"
        assert len(result[0].subject) == 20
