"""Tests for gitlog_digest.file_type_report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.file_type_report import (
    FileTypeEntry,
    _ext,
    build_file_type_map,
    format_file_type_section,
    top_n_types,
)


@dataclass
class FakeCommit:
    hash: str
    author: str
    files_changed: List[str] = field(default_factory=list)


# --- _ext ---

def test_ext_python():
    assert _ext("module/foo.py") == ".py"


def test_ext_no_extension():
    assert _ext("Makefile") == "<no ext>"


def test_ext_uppercase_normalised():
    assert _ext("README.MD") == ".md"


def test_ext_hidden_file_no_ext():
    assert _ext(".gitignore") == "<no ext>"


# --- build_file_type_map ---

def test_empty_commits_returns_empty_map():
    assert build_file_type_map([]) == {}


def test_single_commit_single_file():
    commits = [FakeCommit("abc", "Alice", ["foo.py"])]
    result = build_file_type_map(commits)
    assert ".py" in result
    assert result[".py"].file_count == 1
    assert result[".py"].commit_count == 1


def test_duplicate_file_across_commits_counted_once_per_commit():
    commits = [
        FakeCommit("a1", "Alice", ["foo.py"]),
        FakeCommit("a2", "Bob", ["foo.py"]),
    ]
    result = build_file_type_map(commits)
    # same filename but different commits → file_count still 1 (unique path), commits 2
    assert result[".py"].file_count == 1
    assert result[".py"].commit_count == 2


def test_multiple_extensions_tracked_independently():
    commits = [
        FakeCommit("c1", "Alice", ["app.py", "README.md"]),
        FakeCommit("c2", "Bob", ["utils.py"]),
    ]
    result = build_file_type_map(commits)
    assert result[".py"].file_count == 2
    assert result[".md"].file_count == 1


def test_authors_collected_per_extension():
    commits = [
        FakeCommit("d1", "Alice", ["a.js"]),
        FakeCommit("d2", "Bob", ["b.js"]),
    ]
    result = build_file_type_map(commits)
    assert sorted(result[".js"].authors) == ["Alice", "Bob"]


def test_no_files_changed_attribute_skipped():
    """Commits with no files_changed list should not raise."""
    commits = [FakeCommit("e1", "Alice", [])]
    result = build_file_type_map(commits)
    assert result == {}


# --- top_n_types ---

def test_top_n_limits_results():
    mapping = {
        f".ext{i}": FileTypeEntry(f".ext{i}", i, 1) for i in range(1, 6)
    }
    top = top_n_types(mapping, n=3)
    assert len(top) == 3
    assert top[0].file_count == 5


def test_top_n_larger_than_entries_returns_all():
    mapping = {".py": FileTypeEntry(".py", 3, 2)}
    assert len(top_n_types(mapping, n=10)) == 1


# --- format_file_type_section ---

def test_format_empty_returns_empty_string():
    assert format_file_type_section([]) == ""


def test_format_contains_extension():
    entries = [FileTypeEntry(".py", 5, 3)]
    output = format_file_type_section(entries)
    assert ".py" in output


def test_format_contains_file_count():
    entries = [FileTypeEntry(".ts", 7, 2)]
    output = format_file_type_section(entries)
    assert "7" in output


def test_format_bar_present():
    entries = [FileTypeEntry(".rs", 4, 1)]
    output = format_file_type_section(entries)
    assert "[" in output and "]" in output
