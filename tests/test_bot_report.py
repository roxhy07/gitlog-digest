"""Tests for gitlog_digest.bot_report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.bot_report import (
    BotEntry,
    build_bot_map,
    format_bot_section,
    is_bot_author,
    top_bots,
)


@dataclass
class FakeCommit:
    author: str
    subject: str
    files_changed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# is_bot_author
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "dependabot[bot]",
    "renovate-bot",
    "github-actions[bot]",
    "snyk-bot",
    "my-ci-runner",
    "automation-service",
])
def test_known_bot_names_detected(name):
    assert is_bot_author(name) is True


@pytest.mark.parametrize("name", [
    "Alice",
    "Bob Smith",
    "carol@example.com",
])
def test_human_names_not_detected(name):
    assert is_bot_author(name) is False


def test_case_insensitive_detection():
    assert is_bot_author("Dependabot[BOT]") is True


# ---------------------------------------------------------------------------
# build_bot_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty_map():
    assert build_bot_map([]) == {}


def test_human_only_commits_returns_empty_map():
    commits = [FakeCommit(author="Alice", subject="fix typo")]
    assert build_bot_map(commits) == {}


def test_single_bot_commit_captured():
    commits = [FakeCommit(author="dependabot[bot]", subject="bump lodash")]
    result = build_bot_map(commits)
    assert "dependabot[bot]" in result
    assert result["dependabot[bot]"].commit_count == 1
    assert result["dependabot[bot]"].subjects == ["bump lodash"]


def test_multiple_commits_same_bot_aggregated():
    commits = [
        FakeCommit(author="renovate-bot", subject="update dep A"),
        FakeCommit(author="renovate-bot", subject="update dep B"),
    ]
    result = build_bot_map(commits)
    assert result["renovate-bot"].commit_count == 2
    assert len(result["renovate-bot"].subjects) == 2


def test_mixed_commits_only_bots_in_map():
    commits = [
        FakeCommit(author="Alice", subject="refactor"),
        FakeCommit(author="dependabot[bot]", subject="bump requests"),
    ]
    result = build_bot_map(commits)
    assert list(result.keys()) == ["dependabot[bot]"]


# ---------------------------------------------------------------------------
# top_bots
# ---------------------------------------------------------------------------

def test_top_bots_sorted_by_count():
    entries = {
        "bot-a": BotEntry(author="bot-a", commit_count=3),
        "bot-b": BotEntry(author="bot-b", commit_count=10),
        "bot-c": BotEntry(author="bot-c", commit_count=1),
    }
    result = top_bots(entries, n=2)
    assert [e.author for e in result] == ["bot-b", "bot-a"]


def test_top_bots_respects_n_limit():
    entries = {f"bot-{i}": BotEntry(author=f"bot-{i}", commit_count=i) for i in range(10)}
    assert len(top_bots(entries, n=3)) == 3


# ---------------------------------------------------------------------------
# format_bot_section
# ---------------------------------------------------------------------------

def test_format_empty_map_returns_empty_string():
    assert format_bot_section({}) == ""


def test_format_includes_author_name():
    entries = {"dependabot[bot]": BotEntry(author="dependabot[bot]", commit_count=2, subjects=["bump x", "bump y"])}
    out = format_bot_section(entries)
    assert "dependabot[bot]" in out


def test_format_shows_commit_count():
    entries = {"renovate-bot": BotEntry(author="renovate-bot", commit_count=4, subjects=["s"] * 4)}
    out = format_bot_section(entries)
    assert "4 commit" in out


def test_format_truncates_subjects_after_three():
    subjects = [f"subject {i}" for i in range(6)]
    entries = {"bot-ci": BotEntry(author="bot-ci", commit_count=6, subjects=subjects)}
    out = format_bot_section(entries)
    assert "and 3 more" in out
