"""Tests for gitlog_digest.night_owl_report."""

import pytest
from gitlog_digest.night_owl_report import (
    NightOwlEntry,
    _classify_hour,
    build_night_owl_map,
    top_night_owls,
    format_night_owl_section,
)


class FakeCommit:
    def __init__(self, author: str, date: str):
        self.author = author
        self.date = date


# ---------------------------------------------------------------------------
# _classify_hour
# ---------------------------------------------------------------------------

def test_classify_working_hours():
    assert _classify_hour(10) == "working_hours"

def test_classify_after_hours():
    assert _classify_hour(19) == "after_hours"

def test_classify_late_night_evening():
    assert _classify_hour(23) == "late_night"

def test_classify_late_night_early_morning():
    assert _classify_hour(3) == "late_night"

def test_classify_early_bird():
    assert _classify_hour(7) == "early_bird"

def test_classify_boundary_work_start():
    assert _classify_hour(9) == "working_hours"

def test_classify_boundary_after_hours_start():
    assert _classify_hour(18) == "after_hours"

def test_classify_boundary_late_night_start():
    assert _classify_hour(22) == "late_night"


# ---------------------------------------------------------------------------
# build_night_owl_map
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty():
    assert build_night_owl_map([]) == {}

def test_working_hours_commit_not_counted_as_off_hours():
    commits = [FakeCommit("alice", "2024-03-11T10:30:00")]
    result = build_night_owl_map(commits)
    assert result["alice"].off_hours_total == 0

def test_late_night_commit_counted():
    commits = [FakeCommit("bob", "2024-03-11T23:15:00")]
    result = build_night_owl_map(commits)
    assert result["bob"].late_night_count == 1

def test_early_morning_counted_as_late_night():
    commits = [FakeCommit("bob", "2024-03-12T02:00:00")]
    result = build_night_owl_map(commits)
    assert result["bob"].late_night_count == 1

def test_after_hours_commit_counted():
    commits = [FakeCommit("carol", "2024-03-11T19:45:00")]
    result = build_night_owl_map(commits)
    assert result["carol"].after_hours_count == 1

def test_early_bird_commit_counted():
    commits = [FakeCommit("dave", "2024-03-11T07:10:00")]
    result = build_night_owl_map(commits)
    assert result["dave"].early_bird_count == 1

def test_multiple_commits_accumulated():
    commits = [
        FakeCommit("alice", "2024-03-11T23:00:00"),
        FakeCommit("alice", "2024-03-12T01:00:00"),
        FakeCommit("alice", "2024-03-11T19:00:00"),
    ]
    result = build_night_owl_map(commits)
    assert result["alice"].late_night_count == 2
    assert result["alice"].after_hours_count == 1
    assert result["alice"].commit_count == 3

def test_sample_times_capped_at_three():
    commits = [FakeCommit("eve", f"2024-03-11T2{i}:00:00") for i in range(4)]
    result = build_night_owl_map(commits)
    assert len(result["eve"].sample_times) <= 3

def test_invalid_date_skips_classification():
    commits = [FakeCommit("frank", "not-a-date")]
    result = build_night_owl_map(commits)
    assert result["frank"].commit_count == 1
    assert result["frank"].off_hours_total == 0


# ---------------------------------------------------------------------------
# top_night_owls
# ---------------------------------------------------------------------------

def test_top_night_owls_sorted_by_off_hours():
    mapping = {
        "a": NightOwlEntry("a", commit_count=5, late_night_count=1),
        "b": NightOwlEntry("b", commit_count=3, after_hours_count=4),
        "c": NightOwlEntry("c", commit_count=2, early_bird_count=2),
    }
    top = top_night_owls(mapping, n=3)
    assert top[0].author == "b"
    assert top[1].author == "c"
    assert top[2].author == "a"

def test_top_night_owls_excludes_zero_off_hours():
    mapping = {
        "x": NightOwlEntry("x", commit_count=10),
    }
    assert top_night_owls(mapping) == []

def test_top_night_owls_respects_n():
    mapping = {str(i): NightOwlEntry(str(i), late_night_count=i) for i in range(1, 8)}
    assert len(top_night_owls(mapping, n=3)) == 3


# ---------------------------------------------------------------------------
# format_night_owl_section
# ---------------------------------------------------------------------------

def test_format_empty_returns_empty_string():
    assert format_night_owl_section({}) == ""

def test_format_contains_author_name():
    mapping = {"grace": NightOwlEntry("grace", late_night_count=3)}
    output = format_night_owl_section(mapping)
    assert "grace" in output

def test_format_contains_header():
    mapping = {"heidi": NightOwlEntry("heidi", after_hours_count=2)}
    output = format_night_owl_section(mapping)
    assert "Night Owl" in output

def test_format_shows_off_hours_total():
    mapping = {"ivan": NightOwlEntry("ivan", late_night_count=5)}
    output = format_night_owl_section(mapping)
    assert "off-hours=5" in output
