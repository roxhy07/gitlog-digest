"""Tests for gitlog_digest.tag_report."""

from __future__ import annotations

from gitlog_digest.tag_report import TagEntry, fetch_tags_in_range, format_tag_report
from unittest.mock import patch


def make_tag(name="v1.0.0", sha="abc1234", subject="Release 1.0", date="2024-03-15"):
    return TagEntry(name=name, sha=sha, subject=subject, date=date)


# ---------------------------------------------------------------------------
# TagEntry
# ---------------------------------------------------------------------------

class TestTagEntry:
    def test_fields_stored(self):
        t = make_tag()
        assert t.name == "v1.0.0"
        assert t.sha == "abc1234"
        assert t.subject == "Release 1.0"
        assert t.date == "2024-03-15"


# ---------------------------------------------------------------------------
# format_tag_report
# ---------------------------------------------------------------------------

class TestFormatTagReport:
    def test_empty_list_returns_empty_string(self):
        assert format_tag_report([]) == ""

    def test_contains_tag_name(self):
        report = format_tag_report([make_tag(name="v2.0.0")])
        assert "v2.0.0" in report

    def test_contains_short_sha(self):
        report = format_tag_report([make_tag(sha="deadbeef")])
        assert "deadbeef" in report

    def test_contains_subject(self):
        report = format_tag_report([make_tag(subject="Big release")])
        assert "Big release" in report

    def test_contains_date(self):
        report = format_tag_report([make_tag(date="2024-06-01")])
        assert "2024-06-01" in report

    def test_default_header_level_is_h2(self):
        report = format_tag_report([make_tag()])
        assert report.startswith("## Tags")

    def test_custom_header_level(self):
        report = format_tag_report([make_tag()], header_level=3)
        assert report.startswith("### Tags")

    def test_count_in_header(self):
        tags = [make_tag(name=f"v{i}") for i in range(3)]
        report = format_tag_report(tags)
        assert "Tags (3)" in report

    def test_multiple_tags_all_present(self):
        tags = [make_tag(name="v1.0"), make_tag(name="v2.0")]
        report = format_tag_report(tags)
        assert "v1.0" in report
        assert "v2.0" in report


# ---------------------------------------------------------------------------
# fetch_tags_in_range  (mocked subprocess)
# ---------------------------------------------------------------------------

RAW_OUTPUT = "v1.2.0\tabc1234\tHotfix release\t2024-03-20"


def test_fetch_returns_tag_entries():
    with patch("gitlog_digest.tag_report._run_git", return_value=RAW_OUTPUT):
        tags = fetch_tags_in_range()
    assert len(tags) == 1
    assert tags[0].name == "v1.2.0"


def test_fetch_filters_by_since():
    with patch("gitlog_digest.tag_report._run_git", return_value=RAW_OUTPUT):
        tags = fetch_tags_in_range(since="2024-04-01")
    assert tags == []


def test_fetch_filters_by_until():
    with patch("gitlog_digest.tag_report._run_git", return_value=RAW_OUTPUT):
        tags = fetch_tags_in_range(until="2024-03-01")
    assert tags == []


def test_fetch_empty_output_returns_empty_list():
    with patch("gitlog_digest.tag_report._run_git", return_value=""):
        tags = fetch_tags_in_range()
    assert tags == []
