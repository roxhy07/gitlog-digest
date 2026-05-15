"""Tests for gitlog_digest.revert_report and revert_cli."""
from __future__ import annotations

import argparse
from types import SimpleNamespace
from typing import List

import pytest

from gitlog_digest.revert_report import (
    RevertEntry,
    build_revert_entries,
    format_revert_section,
    is_revert_commit,
    _extract_reverted_hash,
)
from gitlog_digest.revert_cli import (
    add_revert_flag,
    maybe_render_revert,
    revert_summary_line,
)


def make_commit(subject='fix: something', author='Alice', hash='abc1234', body=''):
    return SimpleNamespace(subject=subject, author=author, hash=hash, body=body)


# ---------------------------------------------------------------------------
# is_revert_commit
# ---------------------------------------------------------------------------

def test_revert_prefix_detected():
    assert is_revert_commit('Revert "fix: bad change"') is True

def test_revert_lowercase_detected():
    assert is_revert_commit('revert some commit') is True

def test_non_revert_not_detected():
    assert is_revert_commit('feat: add new thing') is False

def test_empty_subject_not_detected():
    assert is_revert_commit('') is False


# ---------------------------------------------------------------------------
# _extract_reverted_hash
# ---------------------------------------------------------------------------

def test_extracts_sha_from_body():
    body = 'This reverts commit a1b2c3d4e5f6.'
    assert _extract_reverted_hash(body) == 'a1b2c3d4e5f6'

def test_returns_none_when_no_sha():
    assert _extract_reverted_hash('No hash here.') is None

def test_returns_none_for_empty_body():
    assert _extract_reverted_hash('') is None


# ---------------------------------------------------------------------------
# build_revert_entries
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty():
    assert build_revert_entries([]) == []

def test_non_revert_commits_excluded():
    commits = [make_commit('feat: add thing'), make_commit('fix: oops')]
    assert build_revert_entries(commits) == []

def test_revert_commit_included():
    c = make_commit('Revert "fix: oops"', hash='dead001', body='This reverts commit abc1234.')
    entries = build_revert_entries([c])
    assert len(entries) == 1
    assert entries[0].hash == 'dead001'
    assert entries[0].reverted_hash == 'abc1234'

def test_mixed_commits_only_reverts_returned():
    commits = [
        make_commit('feat: new'),
        make_commit('Revert "feat: new"', hash='fff0001'),
        make_commit('chore: lint'),
    ]
    entries = build_revert_entries(commits)
    assert len(entries) == 1
    assert entries[0].hash == 'fff0001'


# ---------------------------------------------------------------------------
# format_revert_section
# ---------------------------------------------------------------------------

def test_empty_entries_returns_empty_string():
    assert format_revert_section([]) == ''

def test_section_contains_header():
    e = RevertEntry(author='Bob', subject='Revert x', hash='aabbccd')
    out = format_revert_section([e])
    assert 'Revert Commits' in out

def test_section_shows_total():
    entries = [RevertEntry(author='A', subject='Revert x', hash='0000001')] * 3
    out = format_revert_section(entries)
    assert 'Total reverts: 3' in out

def test_top_n_limits_rows():
    entries = [RevertEntry(author='A', subject=f'Revert {i}', hash=f'000000{i}') for i in range(5)]
    out = format_revert_section(entries, top_n=2)
    # Only first 2 hashes should appear
    assert '0000000' in out
    assert '0000001' in out
    assert '0000002' not in out


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_parser():
    p = argparse.ArgumentParser()
    add_revert_flag(p)
    return p

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.revert is False

def test_flag_enabled():
    args = _make_parser().parse_args(['--revert'])
    assert args.revert is True

def test_top_reverts_default():
    args = _make_parser().parse_args([])
    assert args.top_reverts == 10

def test_maybe_render_returns_empty_when_flag_off():
    args = _make_parser().parse_args([])
    commits = [make_commit('Revert x')]
    assert maybe_render_revert(args, commits) == ''

def test_maybe_render_returns_section_when_flag_on():
    args = _make_parser().parse_args(['--revert'])
    commits = [make_commit('Revert "fix: oops"', hash='abcdef1')]
    out = maybe_render_revert(args, commits)
    assert 'Revert Commits' in out

def test_revert_summary_line_none():
    assert revert_summary_line([]) == 'No revert commits.'

def test_revert_summary_line_singular():
    assert revert_summary_line([make_commit('Revert x')]) == '1 revert detected.'

def test_revert_summary_line_plural():
    commits = [make_commit('Revert x'), make_commit('Revert y')]
    assert revert_summary_line(commits) == '2 reverts detected.'
