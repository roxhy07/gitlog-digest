"""Git hook installer for gitlog-digest.

Installs a post-commit hook that optionally invalidates the local
digest cache whenever new commits land in the repository.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

HOOK_SCRIPT = """#!/bin/sh
# Installed by gitlog-digest — clears digest cache on new commits.
if command -v gitlog-digest > /dev/null 2>&1; then
    gitlog-digest cache clear --quiet 2>/dev/null || true
fi
"""

HOOK_FILENAME = "post-commit"


def hooks_dir(repo_path: str | Path) -> Path:
    """Return the .git/hooks directory for *repo_path*."""
    return Path(repo_path) / ".git" / "hooks"


def hook_path(repo_path: str | Path) -> Path:
    """Return the full path to the post-commit hook file."""
    return hooks_dir(repo_path) / HOOK_FILENAME


def is_installed(repo_path: str | Path) -> bool:
    """Return True when the gitlog-digest hook is present in *repo_path*."""
    p = hook_path(repo_path)
    if not p.exists():
        return False
    return "gitlog-digest" in p.read_text()


def install_hook(repo_path: str | Path) -> Path:
    """Write the post-commit hook and make it executable.

    If an existing hook is found that was *not* installed by gitlog-digest,
    the gitlog-digest lines are appended rather than overwriting the file.

    Returns the path to the hook file.
    """
    p = hook_path(repo_path)
    hooks_dir(repo_path).mkdir(parents=True, exist_ok=True)

    if p.exists():
        existing = p.read_text()
        if "gitlog-digest" in existing:
            return p  # already installed, nothing to do
        # Append to existing hook
        with p.open("a") as fh:
            fh.write("\n" + HOOK_SCRIPT)
    else:
        p.write_text(HOOK_SCRIPT)

    # Ensure executable bit is set
    current = stat.S_IMODE(os.stat(p).st_mode)
    p.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return p


def uninstall_hook(repo_path: str | Path) -> bool:
    """Remove gitlog-digest lines from the post-commit hook.

    If the hook becomes empty (or only a shebang) after removal it is
    deleted entirely.  Returns True when any change was made.
    """
    p = hook_path(repo_path)
    if not p.exists():
        return False

    original = p.read_text()
    if "gitlog-digest" not in original:
        return False

    # Strip the injected block
    lines = [
        line for line in original.splitlines(keepends=True)
        if "gitlog-digest" not in line
    ]
    cleaned = "".join(lines).strip()
    if cleaned in ("", "#!/bin/sh"):
        p.unlink()
    else:
        p.write_text(cleaned + "\n")
    return True
