"""Generates a code review activity report from commit metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from gitlog_digest.git_parser import Commit


@dataclass
class ReviewEntry:
    author: str
    commit_count: int
    files_touched: int
    subjects: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ReviewEntry(author={self.author!r}, "
            f"commits={self.commit_count}, files={self.files_touched})"
        )


def build_review_entries(commits: List[Commit]) -> List[ReviewEntry]:
    """Aggregate commits into per-author ReviewEntry objects."""
    buckets: Dict[str, dict] = {}
    for commit in commits:
        entry = buckets.setdefault(
            commit.author,
            {"commit_count": 0, "files": set(), "subjects": []},
        )
        entry["commit_count"] += 1
        entry["files"].update(commit.files_changed)
        entry["subjects"].append(commit.subject)

    return [
        ReviewEntry(
            author=author,
            commit_count=data["commit_count"],
            files_touched=len(data["files"]),
            subjects=data["subjects"],
        )
        for author, data in sorted(buckets.items(), key=lambda kv: -kv[1]["commit_count"])
    ]


def _review_bar(value: int, max_value: int, width: int = 20) -> str:
    """Return a simple ASCII bar proportional to value/max_value."""
    if max_value == 0:
        return " " * width
    filled = round(width * value / max_value)
    return "#" * filled + "-" * (width - filled)


def format_review_section(entries: List[ReviewEntry]) -> str:
    """Render the review report as a plain-text section."""
    if not entries:
        return ""

    max_commits = max(e.commit_count for e in entries)
    lines = ["## Code Review Activity", ""]
    for entry in entries:
        bar = _review_bar(entry.commit_count, max_commits)
        lines.append(
            f"  {entry.author:<20} [{bar}] "
            f"{entry.commit_count} commit(s), {entry.files_touched} file(s)"
        )
    lines.append("")
    return "\n".join(lines)
