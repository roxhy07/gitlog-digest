"""Tests for summarizer.py and formatter.py."""

from datetime import date
from unittest.mock import patch

import pytest

from gitlog_digest.formatter import format_author_section, format_digest
from gitlog_digest.git_parser import Commit
from gitlog_digest.summarizer import (
    AuthorSummary,
    WeeklyDigest,
    build_author_summary,
    build_digest,
)


def make_commit(subject="fix bug", author="dev", files=None):
    return Commit(
        hash="abc1234567",
        author=author,
        date="2024-01-15",
        subject=subject,
        files_changed=files or [],
    )


class TestBuildAuthorSummary:
    def test_commit_count(self):
        commits = [make_commit(), make_commit(subject="add feature")]
        summary = build_author_summary("dev", commits)
        assert summary.commit_count == 2

    def test_subjects_collected(self):
        commits = [make_commit(subject="fix A"), make_commit(subject="fix B")]
        summary = build_author_summary("dev", commits)
        assert summary.subjects == ["fix A", "fix B"]

    def test_files_flattened(self):
        commits = [
            make_commit(files=["a.py", "b.py"]),
            make_commit(files=["c.py"]),
        ]
        summary = build_author_summary("dev", commits)
        assert summary.files_changed == ["a.py", "b.py", "c.py"]

    def test_unique_files_deduped(self):
        commits = [make_commit(files=["a.py"]), make_commit(files=["a.py", "b.py"])]
        summary = build_author_summary("dev", commits)
        assert summary.unique_files() == ["a.py", "b.py"]


class TestBuildDigest:
    def test_week_end_is_six_days_after_start(self):
        start = date(2024, 1, 15)
        digest = build_digest([], week_start=start)
        assert digest.week_end == date(2024, 1, 21)

    def test_total_commits(self):
        commits = [make_commit(author="alice"), make_commit(author="bob")]
        digest = build_digest(commits, week_start=date(2024, 1, 15))
        assert digest.total_commits == 2

    def test_authors_sorted(self):
        commits = [make_commit(author="zara"), make_commit(author="alice")]
        digest = build_digest(commits, week_start=date(2024, 1, 15))
        assert [s.author for s in digest.author_summaries] == ["alice", "zara"]

    def test_defaults_to_current_week(self):
        with patch("gitlog_digest.summarizer.date") as mock_date:
            mock_date.today.return_value = date(2024, 1, 17)  # Wednesday
            mock_date.side_effect = lambda *a, **k: date(*a, **k)
            digest = build_digest([])
        assert digest.week_start == date(2024, 1, 15)


class TestFormatter:
    def test_format_digest_contains_header(self):
        digest = WeeklyDigest(
            week_start=date(2024, 1, 15),
            week_end=date(2024, 1, 21),
        )
        output = format_digest(digest)
        assert "Weekly Git Digest" in output
        assert "Jan 15" in output

    def test_empty_digest_message(self):
        digest = WeeklyDigest(week_start=date(2024, 1, 15), week_end=date(2024, 1, 21))
        assert "No commits found" in format_digest(digest)

    def test_author_section_truncates_subjects(self):
        summary = AuthorSummary(
            author="alice",
            commit_count=7,
            subjects=[f"commit {i}" for i in range(7)],
        )
        output = format_author_section(summary)
        assert "and 2 more" in output

    def test_author_section_shows_unique_files(self):
        summary = AuthorSummary(
            author="bob",
            commit_count=1,
            files_changed=["main.py", "utils.py"],
            subjects=["refactor"],
        )
        output = format_author_section(summary)
        assert "main.py" in output
        assert "utils.py" in output
