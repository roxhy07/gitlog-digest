"""Report identifying each author's first commit in the given range."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from gitlog_digest.git_parser import Commit


@dataclass
class FirstCommitEntry:
    author: str
    hash: str
    date: datetime
    subject: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FirstCommitEntry(author={self.author!r}, "
            f"hash={self.hash[:7]!r}, date={self.date.date()})"
        )


def build_first_commit_map(
    commits: List[Commit],
) -> Dict[str, FirstCommitEntry]:
    """Return a mapping of author -> their earliest commit in *commits*."""
    earliest: Dict[str, FirstCommitEntry] = {}
    for commit in commits:
        author = commit.author
        if author not in earliest or commit.date < earliest[author].date:
            earliest[author] = FirstCommitEntry(
                author=author,
                hash=commit.hash,
                date=commit.date,
                subject=commit.subject,
            )
    return earliest


def new_contributors(
    commits: List[Commit],
    known_authors: Optional[List[str]] = None,
) -> List[FirstCommitEntry]:
    """Return entries for authors who are *not* in *known_authors*.

    If *known_authors* is None every author is treated as new.
    """
    known = {a.lower() for a in (known_authors or [])}
    first_map = build_first_commit_map(commits)
    result = [
        entry
        for author, entry in first_map.items()
        if author.lower() not in known
    ]
    return sorted(result, key=lambda e: e.date)


def format_first_commit_section(
    entries: List[FirstCommitEntry],
    *,
    header: str = "## New Contributors",
) -> str:
    """Render a markdown/plain section listing first-time contributors."""
    if not entries:
        return ""
    lines = [header, ""]
    for entry in entries:
        date_str = entry.date.strftime("%Y-%m-%d")
        lines.append(
            f"- **{entry.author}** — first commit on {date_str}: "
            f"`{entry.hash[:7]}` {entry.subject}"
        )
    return "\n".join(lines)
