"""Tests for gitlog_digest.time_zone_report."""

from __future__ import annotations

import pytest

from gitlog_digest.time_zone_report import (
    TimeZoneEntry,
    _extract_offset,
    build_time_zone_map,
    format_time_zone_section,
)


class FakeCommit:
    def __init__(self, author: str, date: str):
        self.author = author
        self.date = date


# ---------------------------------------------------------------------------
# _extract_offset
# ---------------------------------------------------------------------------

class TestExtractOffset:
    def test_colon_form(self):
        assert _extract_offset("2024-03-15T09:42:00+02:00") == "+0200"

    def test_compact_form(self):
        assert _extract_offset("2024-03-15T09:42:00+0530") == "+0530"

    def test_negative_offset(self):
        assert _extract_offset("2024-03-15T14:00:00-05:00") == "-0500"

    def test_utc_zero(self):
        assert _extract_offset("2024-03-15T12:00:00+00:00") == "+0000"

    def test_space_separator(self):
        assert _extract_offset("2024-03-15 09:42:00+02:00") == "+0200"

    def test_empty_string_returns_none(self):
        assert _extract_offset("") is None

    def test_no_offset_returns_none(self):
        assert _extract_offset("2024-03-15T09:42:00") is None


# ---------------------------------------------------------------------------
# TimeZoneEntry
# ---------------------------------------------------------------------------

class TestTimeZoneEntry:
    def test_primary_offset_most_common(self):
        entry = TimeZoneEntry(author="Alice", offsets=["+0200", "+0200", "-0500"])
        assert entry.primary_offset == "+0200"

    def test_primary_offset_none_when_empty(self):
        entry = TimeZoneEntry(author="Bob")
        assert entry.primary_offset is None

    def test_unique_offsets_preserves_order(self):
        entry = TimeZoneEntry(author="Carol", offsets=["+0200", "-0500", "+0200"])
        assert entry.unique_offsets == ["+0200", "-0500"]

    def test_unique_offsets_empty(self):
        entry = TimeZoneEntry(author="Dave")
        assert entry.unique_offsets == []


# ---------------------------------------------------------------------------
# build_time_zone_map
# ---------------------------------------------------------------------------

class TestBuildTimeZoneMap:
    def test_empty_commits_returns_empty(self):
        assert build_time_zone_map([]) == {}

    def test_single_commit(self):
        commits = [FakeCommit("Alice", "2024-03-15T09:00:00+02:00")]
        result = build_time_zone_map(commits)
        assert "Alice" in result
        assert result["Alice"].primary_offset == "+0200"

    def test_multiple_commits_same_author(self):
        commits = [
            FakeCommit("Alice", "2024-03-15T09:00:00+02:00"),
            FakeCommit("Alice", "2024-03-16T10:00:00+02:00"),
            FakeCommit("Alice", "2024-03-17T22:00:00-05:00"),
        ]
        result = build_time_zone_map(commits)
        assert result["Alice"].primary_offset == "+0200"
        assert len(result["Alice"].offsets) == 3

    def test_multiple_authors(self):
        commits = [
            FakeCommit("Alice", "2024-03-15T09:00:00+02:00"),
            FakeCommit("Bob", "2024-03-15T14:00:00-05:00"),
        ]
        result = build_time_zone_map(commits)
        assert set(result.keys()) == {"Alice", "Bob"}

    def test_unparseable_date_skips_offset(self):
        commits = [FakeCommit("Alice", "not-a-date")]
        result = build_time_zone_map(commits)
        assert result["Alice"].offsets == []


# ---------------------------------------------------------------------------
# format_time_zone_section
# ---------------------------------------------------------------------------

class TestFormatTimeZoneSection:
    def test_empty_returns_empty_string(self):
        assert format_time_zone_section({}) == ""

    def test_contains_header(self):
        commits = [FakeCommit("Alice", "2024-03-15T09:00:00+02:00")]
        result = format_time_zone_section(build_time_zone_map(commits))
        assert "## Time Zone Overview" in result

    def test_shows_author_and_offset(self):
        commits = [FakeCommit("Alice", "2024-03-15T09:00:00+02:00")]
        result = format_time_zone_section(build_time_zone_map(commits))
        assert "Alice" in result
        assert "+0200" in result

    def test_multiple_offsets_shown(self):
        commits = [
            FakeCommit("Bob", "2024-03-15T09:00:00+02:00"),
            FakeCommit("Bob", "2024-03-16T22:00:00-05:00"),
        ]
        result = format_time_zone_section(build_time_zone_map(commits))
        assert "also seen" in result

    def test_top_n_limits_output(self):
        commits = [FakeCommit(f"Author{i}", "2024-03-15T09:00:00+00:00") for i in range(20)]
        result = format_time_zone_section(build_time_zone_map(commits), top_n=5)
        count = sum(1 for line in result.splitlines() if line.strip().startswith("Author"))
        assert count == 5
