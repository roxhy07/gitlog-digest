"""Tests for the CLI argument parsing and date resolution logic."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from gitlog_digest.cli import parse_args, resolve_dates, main


class TestParseArgs:
    def test_defaults(self):
        args = parse_args([])
        assert args.repo == "."
        assert args.since is None
        assert args.until is None
        assert args.output is None
        assert args.branch == "HEAD"

    def test_repo_positional(self):
        args = parse_args(["/some/repo"])
        assert args.repo == "/some/repo"

    def test_since_until_flags(self):
        args = parse_args(["--since", "2024-01-01", "--until", "2024-01-07"])
        assert args.since == "2024-01-01"
        assert args.until == "2024-01-07"

    def test_output_short_flag(self):
        args = parse_args(["-o", "out.md"])
        assert args.output == "out.md"

    def test_branch_flag(self):
        args = parse_args(["--branch", "main"])
        assert args.branch == "main"


class TestResolveDates:
    def test_explicit_dates(self):
        since, until = resolve_dates("2024-03-01", "2024-03-07")
        assert since == "2024-03-01"
        assert until == "2024-03-07"

    def test_defaults_to_last_7_days(self):
        since, until = resolve_dates(None, None)
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        assert until == str(today)
        assert since == str(today - timedelta(days=7))

    def test_only_since_provided(self):
        since, until = resolve_dates("2024-06-01", None)
        from datetime import datetime
        today = str(datetime.utcnow().date())
        assert since == "2024-06-01"
        assert until == today


class TestMain:
    def test_exits_if_not_git_repo(self, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            main([str(tmp_path)])
        assert exc_info.value.code == 1

    def test_exits_zero_on_no_commits(self, tmp_path, capsys):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        with patch("gitlog_digest.cli.fetch_commits", return_value=[]):
            with pytest.raises(SystemExit) as exc_info:
                main([str(tmp_path)])
            assert exc_info.value.code == 0

    def test_prints_digest_to_stdout(self, tmp_path, capsys):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        mock_commit = MagicMock()
        mock_commit.author = "Alice"
        with patch("gitlog_digest.cli.fetch_commits", return_value=[mock_commit]), \
             patch("gitlog_digest.cli.group_by_author", return_value={"Alice": [mock_commit]}), \
             patch("gitlog_digest.cli.build_author_summary", return_value=MagicMock()), \
             patch("gitlog_digest.cli.format_digest", return_value="## Weekly Digest"):
            main([str(tmp_path)])
        captured = capsys.readouterr()
        assert "Weekly Digest" in captured.out

    def test_writes_output_to_file(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        out_file = tmp_path / "digest.md"
        mock_commit = MagicMock()
        mock_commit.author = "Bob"
        with patch("gitlog_digest.cli.fetch_commits", return_value=[mock_commit]), \
             patch("gitlog_digest.cli.group_by_author", return_value={"Bob": [mock_commit]}), \
             patch("gitlog_digest.cli.build_author_summary", return_value=MagicMock()), \
             patch("gitlog_digest.cli.format_digest", return_value="# Digest Output"):
            main([str(tmp_path), "-o", str(out_file)])
        assert out_file.read_text(encoding="utf-8") == "# Digest Output"
