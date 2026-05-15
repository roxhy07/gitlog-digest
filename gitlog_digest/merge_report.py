"""Detect and summarise merge commits in the git log."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class MergeEntry:
    """Represents a single merge commit."""

    hash: str
    author: str
    subject: str
    date: str
    branches_mentioned: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"MergeEntry({self.hash[:7]!r}, {self.author!r})"


_MERGE_PREFIXES = ("Merge branch", "Merge pull request", "Merge remote-tracking")


def is_merge_commit(subject: str) -> bool:
    """Return True when *subject* looks like an auto-generated merge message."""
    return any(subject.startswith(prefix) for prefix in _MERGE_PREFIXES)


def _extract_branches(subject: str) -> List[str]:
    """Best-effort extraction of branch names quoted with single-quotes."""
    parts: List[str] = []
    for token in subject.split("'"):
        stripped = token.strip()
        if stripped and not stripped.startswith("Merge"):
            parts.append(stripped)
    return parts


def build_merge_entries(commits: Sequence) -> List[MergeEntry]:
    """Filter *commits* to merge commits and build :class:`MergeEntry` objects."""
    entries: List[MergeEntry] = []
    for commit in commits:
        if not is_merge_commit(commit.subject):
            continue
        entries.append(
            MergeEntry(
                hash=commit.hash,
                author=commit.author,
                subject=commit.subject,
                date=commit.date,
                branches_mentioned=_extract_branches(commit.subject),
            )
        )
    return entries


def format_merge_section(entries: List[MergeEntry], top_n: int = 10) -> str:
    """Render a plain-text section listing the most recent merge commits."""
    if not entries:
        return ""
    lines = ["Merge Commits", "=" * 13]
    for entry in entries[:top_n]:
        branches = ", ".join(entry.branches_mentioned) if entry.branches_mentioned else "-"
        lines.append(f"  [{entry.hash[:7]}] {entry.date}  {entry.author}")
        lines.append(f"    {entry.subject}")
        lines.append(f"    branches: {branches}")
    return "\n".join(lines)
