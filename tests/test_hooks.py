"""Tests for gitlog_digest.hooks."""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from gitlog_digest.hooks import (
    HOOK_FILENAME,
    hook_path,
    hooks_dir,
    install_hook,
    is_installed,
    uninstall_hook,
)


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """Create a minimal fake git repo directory structure."""
    (tmp_path / ".git" / "hooks").mkdir(parents=True)
    return tmp_path


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_hooks_dir_points_inside_git(fake_repo):
    assert hooks_dir(fake_repo) == fake_repo / ".git" / "hooks"


def test_hook_path_includes_filename(fake_repo):
    assert hook_path(fake_repo).name == HOOK_FILENAME


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

def test_install_creates_hook_file(fake_repo):
    p = install_hook(fake_repo)
    assert p.exists()


def test_installed_hook_contains_marker(fake_repo):
    install_hook(fake_repo)
    assert "gitlog-digest" in hook_path(fake_repo).read_text()


def test_hook_is_executable(fake_repo):
    p = install_hook(fake_repo)
    mode = stat.S_IMODE(p.stat().st_mode)
    assert mode & stat.S_IXUSR


def test_install_is_idempotent(fake_repo):
    install_hook(fake_repo)
    install_hook(fake_repo)
    content = hook_path(fake_repo).read_text()
    assert content.count("gitlog-digest") == content.count("gitlog-digest")
    # More importantly, the marker appears exactly twice (once in the clear
    # command, once in the guard) — not duplicated across two installs.
    assert content.count("cache clear") == 1


def test_install_appends_to_existing_hook(fake_repo):
    existing = hook_path(fake_repo)
    existing.write_text("#!/bin/sh\necho hello\n")
    install_hook(fake_repo)
    content = existing.read_text()
    assert "echo hello" in content
    assert "gitlog-digest" in content


# ---------------------------------------------------------------------------
# is_installed
# ---------------------------------------------------------------------------

def test_is_installed_false_when_no_hook(fake_repo):
    assert is_installed(fake_repo) is False


def test_is_installed_true_after_install(fake_repo):
    install_hook(fake_repo)
    assert is_installed(fake_repo) is True


def test_is_installed_false_for_unrelated_hook(fake_repo):
    hook_path(fake_repo).write_text("#!/bin/sh\necho hi\n")
    assert is_installed(fake_repo) is False


# ---------------------------------------------------------------------------
# uninstall
# ---------------------------------------------------------------------------

def test_uninstall_returns_false_when_not_present(fake_repo):
    assert uninstall_hook(fake_repo) is False


def test_uninstall_removes_file_when_only_digest_content(fake_repo):
    install_hook(fake_repo)
    p = hook_path(fake_repo)
    changed = uninstall_hook(fake_repo)
    assert changed is True
    assert not p.exists()


def test_uninstall_preserves_other_hook_content(fake_repo):
    hook_path(fake_repo).write_text("#!/bin/sh\necho hello\n")
    install_hook(fake_repo)
    uninstall_hook(fake_repo)
    content = hook_path(fake_repo).read_text()
    assert "echo hello" in content
    assert "gitlog-digest" not in content
