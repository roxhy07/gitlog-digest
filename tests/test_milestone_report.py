"""Tests for gitlog_digest.milestone_report."""

import pytest
from datetime import datetime
from gitlog_digest.git_parser import Commit
from gitlog_digest.milestone_report import (
    Milestone,
    detect_milestones,
    format_milestone_report,
    _milestone_label,
)


def make_commit(subject="fix stuff", author="dev", hash_="abc1234") -> Commit:
    return Commit(
        hash=hash_,
        author=author,
        date=datetime(2024, 1, 15),
        subject=subject,
        files_changed=[],
    )


def _commits(n: int) -> list:
    """Return n commits in newest-first order."""
    return [make_commit(hash_=f"{i:07x}") for i in range(n, 0, -1)]


class TestDetectMilestones:
    def test_empty_list_returns_empty(self):
        assert detect_milestones([]) == []

    def test_first_commit_detected(self):
        commits = _commits(1)
        result = detect_milestones(commits, thresholds={1})
        assert len(result) == 1
        assert result[0].number == 1
        assert result[0].label == "First commit"

    def test_tenth_commit_detected(self):
        commits = _commits(10)
        result = detect_milestones(commits, thresholds={10})
        assert len(result) == 1
        assert result[0].number == 10

    def test_no_milestone_when_threshold_not_reached(self):
        commits = _commits(5)
        result = detect_milestones(commits, thresholds={10})
        assert result == []

    def test_multiple_thresholds_in_range(self):
        commits = _commits(50)
        result = detect_milestones(commits, thresholds={1, 10, 50})
        numbers = [m.number for m in result]
        assert sorted(numbers) == [1, 10, 50]

    def test_correct_commit_attached_to_milestone(self):
        commits = _commits(3)
        # oldest commit is at index -1 (reversed) => number 1
        result = detect_milestones(commits, thresholds={1})
        assert result[0].commit is commits[-1]

    def test_uses_default_thresholds_when_none_given(self):
        commits = _commits(10)
        result = detect_milestones(commits)
        numbers = {m.number for m in result}
        assert 1 in numbers
        assert 10 in numbers


class TestMilestoneLabel:
    def test_first_is_special(self):
        assert _milestone_label(1) == "First commit"

    def test_large_number_formatted_with_comma(self):
        assert _milestone_label(1000) == "Commit #1,000"

    def test_regular_number(self):
        assert _milestone_label(50) == "Commit #50"


class TestFormatMilestoneReport:
    def _milestones(self):
        c = make_commit(subject="initial commit", author="alice", hash_="aaabbbc")
        return [Milestone(number=1, commit=c, label="First commit")]

    def test_empty_returns_empty_string(self):
        assert format_milestone_report([]) == ""

    def test_markdown_has_h2_header(self):
        result = format_milestone_report(self._milestones(), markdown=True)
        assert result.startswith("## Milestones")

    def test_plain_has_dashes(self):
        result = format_milestone_report(self._milestones(), markdown=False)
        assert "----------" in result

    def test_markdown_contains_bold_label(self):
        result = format_milestone_report(self._milestones(), markdown=True)
        assert "**First commit**" in result

    def test_plain_contains_label(self):
        result = format_milestone_report(self._milestones(), markdown=False)
        assert "First commit" in result

    def test_author_appears_in_output(self):
        result = format_milestone_report(self._milestones())
        assert "alice" in result
