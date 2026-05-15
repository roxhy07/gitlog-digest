"""Tests for gitlog_digest.fixup_report and fixup_cli."""
from __future__ import annotations

import argparse
import pytest

from gitlog_digest.fixup_report import (
    is_fixup_commit,
    _classify,
    build_fixup_entries,
    format_fixup_section,
    FixupEntry,
)
from gitlog_digest.fixup_cli import add_fixup_flag, maybe_render_fixup, fixup_summary_line


class FakeCommit:
    def __init__(self, subject: str, author: str = "Dev", hash: str = "abc1234"):
        self.subject = subject
        self.author = author
        self.hash = hash


# ---------------------------------------------------------------------------
# is_fixup_commit
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("subject", [
    "fixup! add tests",
    "squash! rename variable",
    "WIP: half-done feature",
    "[WIP] still working",
    "wip: draft",
    "fix up typo",
    "amend: adjust spacing",
])
def test_known_fixup_subjects_detected(subject):
    assert is_fixup_commit(subject)


@pytest.mark.parametrize("subject", [
    "feat: add login",
    "fix: null pointer",
    "docs: update readme",
    "refactor: extract method",
    "",
])
def test_regular_subjects_not_detected(subject):
    assert not is_fixup_commit(subject)


def test_is_fixup_case_insensitive():
    assert is_fixup_commit("FIXUP! something")
    assert is_fixup_commit("Squash! something")


# ---------------------------------------------------------------------------
# _classify
# ---------------------------------------------------------------------------

def test_classify_squash():
    assert _classify("squash! rename") == "squash"


def test_classify_wip():
    assert _classify("wip: draft") == "wip"
    assert _classify("[WIP] in progress") == "wip"


def test_classify_fixup_default():
    assert _classify("fixup! adjust") == "fixup"
    assert _classify("amend: spacing") == "fixup"


# ---------------------------------------------------------------------------
# build_fixup_entries
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty():
    assert build_fixup_entries([]) == []


def test_non_fixup_commits_excluded():
    commits = [FakeCommit("feat: new thing"), FakeCommit("fix: bug")]
    assert build_fixup_entries(commits) == []


def test_fixup_commit_included():
    commits = [FakeCommit("fixup! typo", author="Alice", hash="deadbeef")]
    result = build_fixup_entries(commits)
    assert len(result) == 1
    assert result[0].author == "Alice"
    assert result[0].kind == "fixup"
    assert result[0].hash == "deadbeef"


def test_mixed_commits_only_fixups_returned():
    commits = [
        FakeCommit("feat: login"),
        FakeCommit("squash! clean up"),
        FakeCommit("docs: readme"),
        FakeCommit("wip: draft"),
    ]
    result = build_fixup_entries(commits)
    assert len(result) == 2
    assert {e.kind for e in result} == {"squash", "wip"}


# ---------------------------------------------------------------------------
# format_fixup_section
# ---------------------------------------------------------------------------

def test_empty_entries_returns_empty_string():
    assert format_fixup_section([]) == ""


def test_section_contains_author_and_subject():
    entries = [FixupEntry(author="Bob", hash="abc1234", subject="fixup! test", kind="fixup")]
    output = format_fixup_section(entries)
    assert "Bob" in output
    assert "fixup! test" in output
    assert "abc1234"[:7] in output


def test_top_n_limits_output():
    entries = [
        FixupEntry(author="Dev", hash=f"{i:07x}", subject=f"fixup! item {i}", kind="fixup")
        for i in range(15)
    ]
    output = format_fixup_section(entries, top_n=5)
    assert "10 more" in output


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_parser():
    p = argparse.ArgumentParser()
    add_fixup_flag(p)
    return p


def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.fixup is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--fixup"])
    assert args.fixup is True


def test_top_fixups_default():
    args = _make_parser().parse_args([])
    assert args.top_fixups == 10


def test_maybe_render_fixup_disabled():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("fixup! something")]
    assert maybe_render_fixup(args, commits) == ""


def test_maybe_render_fixup_enabled():
    args = _make_parser().parse_args(["--fixup"])
    commits = [FakeCommit("fixup! something", author="Alice")]
    result = maybe_render_fixup(args, commits)
    assert "Alice" in result


def test_fixup_summary_line_empty_when_none():
    commits = [FakeCommit("feat: cool")]
    assert fixup_summary_line(commits) == ""


def test_fixup_summary_line_shows_kinds():
    commits = [
        FakeCommit("fixup! a"),
        FakeCommit("fixup! b"),
        FakeCommit("squash! c"),
    ]
    line = fixup_summary_line(commits)
    assert "fixup" in line
    assert "squash" in line
