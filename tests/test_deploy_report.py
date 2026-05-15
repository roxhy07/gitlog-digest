"""Tests for gitlog_digest.deploy_report and deploy_cli."""
from __future__ import annotations

import argparse
import pytest

from gitlog_digest.deploy_report import (
    is_deploy_commit,
    build_deploy_entries,
    format_deploy_section,
    DeployEntry,
)
from gitlog_digest.deploy_cli import (
    add_deploy_flag,
    maybe_render_deploy,
    deploy_summary_line,
)


class FakeCommit:
    def __init__(self, subject: str, author: str = "alice", hash: str = "abc1234", timestamp: str = ""):
        self.subject = subject
        self.author = author
        self.hash = hash
        self.timestamp = timestamp


# --- is_deploy_commit ---

def test_deploy_keyword_detected():
    assert is_deploy_commit("deploy to production") is True

def test_release_keyword_detected():
    assert is_deploy_commit("release v2.3.0") is True

def test_ship_keyword_detected():
    assert is_deploy_commit("ship new feature") is True

def test_rollout_keyword_detected():
    assert is_deploy_commit("rollout canary 10%") is True

def test_publish_keyword_detected():
    assert is_deploy_commit("publish package to npm") is True

def test_regular_commit_not_detected():
    assert is_deploy_commit("fix typo in readme") is False

def test_case_insensitive_deploy():
    assert is_deploy_commit("DEPLOY hotfix") is True


# --- build_deploy_entries ---

def test_empty_commits_returns_empty():
    assert build_deploy_entries([]) == []

def test_single_deploy_commit_returned():
    commits = [FakeCommit("deploy to staging", author="bob", hash="deadbeef")]
    entries = build_deploy_entries(commits)
    assert len(entries) == 1
    assert entries[0].author == "bob"
    assert entries[0].hash == "deadbeef"

def test_non_deploy_commits_excluded():
    commits = [
        FakeCommit("fix bug"),
        FakeCommit("release v1.0"),
        FakeCommit("update docs"),
    ]
    entries = build_deploy_entries(commits)
    assert len(entries) == 1
    assert entries[0].subject == "release v1.0"

def test_multiple_deploy_commits_all_included():
    commits = [
        FakeCommit("deploy api"),
        FakeCommit("deploy frontend"),
    ]
    assert len(build_deploy_entries(commits)) == 2


# --- format_deploy_section ---

def test_empty_entries_returns_empty_string():
    assert format_deploy_section([]) == ""

def test_section_contains_header():
    entries = [DeployEntry(author="alice", hash="abc1234x", subject="deploy v1", timestamp="")]
    result = format_deploy_section(entries)
    assert "Deployments" in result

def test_section_contains_hash_prefix():
    entries = [DeployEntry(author="alice", hash="abc1234x", subject="deploy v1", timestamp="")]
    result = format_deploy_section(entries)
    assert "abc1234" in result

def test_top_n_limits_output():
    entries = [DeployEntry(author="a", hash=f"{i:07d}", subject=f"deploy {i}", timestamp="") for i in range(20)]
    result = format_deploy_section(entries, top_n=5)
    assert result.count("deploy") == 5


# --- deploy_cli ---

def _make_parser():
    p = argparse.ArgumentParser()
    add_deploy_flag(p)
    return p

def test_flag_default_false():
    args = _make_parser().parse_args([])
    assert args.deploy is False

def test_flag_enabled():
    args = _make_parser().parse_args(["--deploy"])
    assert args.deploy is True

def test_top_deploys_default():
    args = _make_parser().parse_args([])
    assert args.top_deploys == 10

def test_maybe_render_deploy_disabled_returns_empty():
    args = _make_parser().parse_args([])
    result = maybe_render_deploy(args, [FakeCommit("deploy stuff")])
    assert result == ""

def test_maybe_render_deploy_enabled_returns_section():
    args = _make_parser().parse_args(["--deploy"])
    result = maybe_render_deploy(args, [FakeCommit("deploy stuff")])
    assert "Deployments" in result

def test_deploy_summary_line_singular():
    line = deploy_summary_line([FakeCommit("deploy v1")])
    assert "1 commit" in line

def test_deploy_summary_line_plural():
    commits = [FakeCommit("deploy v1"), FakeCommit("release v2")]
    line = deploy_summary_line(commits)
    assert "2 commits" in line
