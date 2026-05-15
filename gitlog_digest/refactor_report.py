"""Identifies commits that appear to be refactors based on subject keywords."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

_REFACTOR_KEYWORDS = (
    "refactor",
    "restructure",
    "reorganise",
    "reorganize",
    "cleanup",
    "clean up",
    "tidy",
    "rename",
    "move",
    "extract",
    "simplify",
    "dedup",
    "deduplicate",
)


@dataclass
class RefactorEntry:
    author: str
    subjects: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.subjects)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RefactorEntry(author={self.author!r}, count={self.count})"


def is_refactor_commit(subject: str) -> bool:
    """Return True if the subject line looks like a refactor."""
    lowered = subject.lower()
    return any(kw in lowered for kw in _REFACTOR_KEYWORDS)


def build_refactor_map(commits: Sequence) -> dict[str, RefactorEntry]:
    """Return a mapping of author -> RefactorEntry for refactor-like commits."""
    result: dict[str, RefactorEntry] = {}
    for commit in commits:
        if not is_refactor_commit(commit.subject):
            continue
        entry = result.setdefault(commit.author, RefactorEntry(author=commit.author))
        entry.subjects.append(commit.subject)
    return result


def top_refactorers(refactor_map: dict[str, RefactorEntry], n: int = 5) -> List[RefactorEntry]:
    """Return the top-n authors by refactor commit count."""
    return sorted(refactor_map.values(), key=lambda e: e.count, reverse=True)[:n]


def format_refactor_section(entries: List[RefactorEntry], top_n: int = 5) -> str:
    """Render a plain-text section listing top refactorers."""
    if not entries:
        return ""
    lines = ["Refactor Activity", "-" * 17]
    for entry in entries[:top_n]:
        lines.append(f"  {entry.author}: {entry.count} refactor commit(s)")
        for subj in entry.subjects[:3]:
            lines.append(f"    - {subj}")
        if len(entry.subjects) > 3:
            lines.append(f"    … and {len(entry.subjects) - 3} more")
    return "\n".join(lines)
