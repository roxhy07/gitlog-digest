"""Tests for the git_parser module."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from gitlog_digest.git_parser import Commit, fetch_commits, group_by_author


SAMPLE_LOG = (
    "abc1234def5678|Alice|alice@example.com|2024-01-15 09:30:00 +0000|feat: add login page\n"
    "111aaabbbccc22|Bob|bob@example.com|2024-01-16 14:00:00 +0000|fix: correct typo in README\n"
    "deadbeefcafe33|Alice|alice@example.com|2024-01-17 11:15:00 +0000|chore: update deps\n"
)


def make_commit(hash_="aabbccdd", author="Dev", email="dev@x.com",
                subject="test commit", offset=0) -> Commit:
    dt = datetime(2024, 1, 15 + offset, 10, 0, 0, tzinfo=timezone.utc)
    return Commit(hash=hash_, author_name=author, author_email=email,
                  date=dt, subject=subject)


class TestCommit:
    def test_short_hash(self):
        c = make_commit(hash_="abcdef1234567")
        assert c.short_hash == "abcdef1"

    def test_repr_truncates_long_subject(self):
        c = make_commit(subject="a" * 60)
        assert "..." in repr(c)

    def test_files_changed_defaults_empty(self):
        c = make_commit()
        assert c.files_changed == []


class TestFetchCommits:
    @patch("gitlog_digest.git_parser.subprocess.run")
    def test_parses_commits(self, mock_run):
        mock_run.return_value = MagicMock(stdout=SAMPLE_LOG, returncode=0)
        commits = fetch_commits(repo_path="/fake/repo")
        assert len(commits) == 3
        assert commits[0].author_name == "Alice"
        assert commits[1].subject == "fix: correct typo in README"
        assert commits[2].short_hash == "deadbee"

    @patch("gitlog_digest.git_parser.subprocess.run")
    def test_since_flag_passed(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        fetch_commits(since="2024-01-01")
        cmd = mock_run.call_args[0][0]
        assert "--since=2024-01-01" in cmd

    @patch("gitlog_digest.git_parser.subprocess.run")
    def test_empty_log_returns_empty_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        assert fetch_commits() == []

    @patch("gitlog_digest.git_parser.subprocess.run")
    def test_malformed_line_skipped(self, mock_run):
        mock_run.return_value = MagicMock(stdout="bad line\n" + SAMPLE_LOG, returncode=0)
        commits = fetch_commits()
        assert len(commits) == 3


class TestGroupByAuthor:
    def test_groups_correctly(self):
        commits = [
            make_commit(author="Alice"),
            make_commit(author="Bob"),
            make_commit(author="Alice"),
        ]
        groups = group_by_author(commits)
        assert set(groups.keys()) == {"Alice", "Bob"}
        assert len(groups["Alice"]) == 2
        assert len(groups["Bob"]) == 1

    def test_empty_input(self):
        assert group_by_author([]) == {}
