"""Tests for gitlog_digest.renderer."""

from __future__ import annotations

import pytest

from gitlog_digest.git_parser import Commit
from gitlog_digest.summarizer import WeeklyDigest, build_author_summary
from gitlog_digest.renderer import render, render_markdown, render_plain


def make_commit(
    author: str = "Ada",
    subject: str = "fix: something",
    files: list[str] | None = None,
) -> Commit:
    return Commit(
        hash="abc1234567",
        author=author,
        date="2024-01-15",
        subject=subject,
        files_changed=files or ["src/main.py"],
    )


def _make_digest() -> WeeklyDigest:
    commits = [
        make_commit("Ada", "feat: add parser", ["parser.py"]),
        make_commit("Ada", "fix: edge case", ["parser.py", "utils.py"]),
        make_commit("Bob", "docs: update readme", ["README.md"]),
    ]
    authors = [build_author_summary(a, cs) for a, cs in
               {"Ada": commits[:2], "Bob": commits[2:]}.items()]
    return WeeklyDigest(
        since="2024-01-08",
        until="2024-01-14",
        authors=authors,
        total_commits=3,
        total_authors=2,
    )


class TestRenderMarkdown:
    def test_contains_h1_header(self):
        out = render_markdown(_make_digest())
        assert "# Weekly Digest" in out

    def test_shows_commit_count(self):
        out = render_markdown(_make_digest())
        assert "3 commit(s)" in out

    def test_author_section_h2(self):
        out = render_markdown(_make_digest())
        assert "## Ada" in out
        assert "## Bob" in out

    def test_subjects_listed(self):
        out = render_markdown(_make_digest())
        assert "feat: add parser" in out
        assert "docs: update readme" in out

    def test_date_range_in_header(self):
        out = render_markdown(_make_digest())
        assert "2024-01-08" in out
        assert "2024-01-14" in out


class TestRenderPlain:
    def test_separator_line(self):
        out = render_plain(_make_digest())
        assert "=" * 10 in out

    def test_author_bracket_format(self):
        out = render_plain(_make_digest())
        assert "[Ada]" in out
        assert "[Bob]" in out

    def test_bullet_prefix(self):
        out = render_plain(_make_digest())
        assert "    * feat: add parser" in out


class TestRenderDispatch:
    def test_markdown_dispatch(self):
        out = render(_make_digest(), fmt="markdown")
        assert out.startswith("# Weekly Digest")

    def test_plain_dispatch(self):
        out = render(_make_digest(), fmt="plain")
        assert out.startswith("Weekly Digest")
        assert "#" not in out.splitlines()[0]

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown output format"):
            render(_make_digest(), fmt="html")  # type: ignore[arg-type]
