"""Tests for gitlog_digest.wip_report and wip_cli."""

import argparse
import pytest

from gitlog_digest.wip_report import (
    WipEntry,
    build_wip_entries,
    format_wip_section,
    is_wip_commit,
    _extract_label,
)
from gitlog_digest.wip_cli import add_wip_flag, maybe_render_wip, wip_summary_line


class FakeCommit:
    def __init__(self, subject, author="dev", hash="abc1234567890"):
        self.subject = subject
        self.author = author
        self.hash = hash


# --- is_wip_commit ---

@pytest.mark.parametrize("subject", [
    "WIP: rough draft",
    "draft: not ready",
    "fixme: broken test",
    "HACK around rate limit",
    "temp workaround",
    "TODO remove this",
    "do not merge yet",
    "DNM: experiment",
])
def test_wip_subjects_detected(subject):
    assert is_wip_commit(subject) is True


@pytest.mark.parametrize("subject", [
    "feat: add login page",
    "fix: correct typo",
    "chore: update deps",
    "refactor: clean up auth",
])
def test_regular_subjects_not_wip(subject):
    assert is_wip_commit(subject) is False


def test_is_wip_case_insensitive():
    assert is_wip_commit("wip something") is True
    assert is_wip_commit("WIP something") is True
    assert is_wip_commit("Wip something") is True


# --- _extract_label ---

def test_extract_label_returns_lowercase():
    assert _extract_label("WIP: stuff") == "wip"


def test_extract_label_no_match_returns_empty():
    assert _extract_label("feat: normal commit") == ""


# --- build_wip_entries ---

def test_empty_commits_returns_empty():
    assert build_wip_entries([]) == []


def test_only_wip_commits_included():
    commits = [
        FakeCommit("WIP: half done"),
        FakeCommit("feat: finished thing"),
        FakeCommit("draft: rough idea"),
    ]
    result = build_wip_entries(commits)
    assert len(result) == 2
    assert all(isinstance(e, WipEntry) for e in result)


def test_entry_fields_populated():
    c = FakeCommit("WIP: test", author="alice", hash="deadbeef")
    entries = build_wip_entries([c])
    assert entries[0].author == "alice"
    assert entries[0].label == "wip"
    assert entries[0].hash == "deadbeef"


# --- format_wip_section ---

def test_empty_entries_returns_empty_string():
    assert format_wip_section([]) == ""


def test_section_contains_subject():
    e = WipEntry(hash="abc1234", author="bob", subject="WIP: do thing", label="wip")
    out = format_wip_section([e])
    assert "WIP: do thing" in out


def test_top_n_limits_output():
    entries = [WipEntry(hash="a" * 7, author="x", subject=f"WIP {i}", label="wip") for i in range(20)]
    out = format_wip_section(entries, top_n=5)
    assert "15 more" in out


# --- wip_cli ---

def _make_parser():
    p = argparse.ArgumentParser()
    add_wip_flag(p)
    return p


def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.wip is False


def test_flag_enabled():
    args = _make_parser().parse_args(["--wip"])
    assert args.wip is True


def test_top_wip_default():
    args = _make_parser().parse_args([])
    assert args.top_wip == 10


def test_maybe_render_wip_off_returns_empty():
    args = _make_parser().parse_args([])
    commits = [FakeCommit("WIP: something")]
    assert maybe_render_wip(args, commits) == ""


def test_maybe_render_wip_on_returns_section():
    args = _make_parser().parse_args(["--wip"])
    commits = [FakeCommit("WIP: something")]
    out = maybe_render_wip(args, commits)
    assert "WIP" in out


def test_wip_summary_line_empty():
    assert wip_summary_line([]) == ""


def test_wip_summary_line_singular():
    e = WipEntry(hash="a", author="x", subject="WIP", label="wip")
    assert "1 WIP" in wip_summary_line([e])
    assert "commits" not in wip_summary_line([e])


def test_wip_summary_line_plural():
    entries = [WipEntry(hash="a", author="x", subject="WIP", label="wip")] * 3
    assert "3 WIP" in wip_summary_line(entries)
    assert "commits" in wip_summary_line(entries)
