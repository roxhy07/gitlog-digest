"""Branch activity report: summarise which branches commits landed on."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BranchEntry:
    branch: str
    commit_count: int
    authors: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"BranchEntry(branch={self.branch!r}, "
            f"commits={self.commit_count}, authors={len(self.authors)})"
        )


def _run_git(args: List[str], repo: str = ".") -> str:
    result = subprocess.run(
        ["git", "-C", repo] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def fetch_branch_for_commit(sha: str, repo: str = ".") -> Optional[str]:
    """Return the first branch name that contains *sha*, or None."""
    raw = _run_git(
        ["branch", "--contains", sha, "--format=%(refname:short)"],
        repo=repo,
    )
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    return lines[0] if lines else None


def build_branch_map(commits, repo: str = ".") -> dict:
    """Return a dict mapping branch name -> BranchEntry."""
    entries: dict = {}
    for commit in commits:
        branch = fetch_branch_for_commit(commit.hash, repo)
        if branch is None:
            branch = "(detached)"
        if branch not in entries:
            entries[branch] = BranchEntry(branch=branch, commit_count=0, authors=[])
        entries[branch].commit_count += 1
        if commit.author not in entries[branch].authors:
            entries[branch].authors.append(commit.author)
    return entries


def top_n_branches(branch_map: dict, n: int = 10) -> List[BranchEntry]:
    """Return the top *n* branches sorted by commit count descending."""
    return sorted(branch_map.values(), key=lambda e: e.commit_count, reverse=True)[:n]


def _branch_bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = round(value / max_value * width)
    return "█" * filled + "░" * (width - filled)


def format_branch_section(entries: List[BranchEntry]) -> str:
    """Render a plain-text branch activity section."""
    if not entries:
        return ""
    max_commits = max(e.commit_count for e in entries)
    lines = ["Branch Activity", "---------------"]
    for entry in entries:
        bar = _branch_bar(entry.commit_count, max_commits)
        author_count = len(entry.authors)
        lines.append(
            f"{entry.branch:<30} {bar} {entry.commit_count:>4} commits  "
            f"{author_count} author{'s' if author_count != 1 else ''}"
        )
    return "\n".join(lines)
