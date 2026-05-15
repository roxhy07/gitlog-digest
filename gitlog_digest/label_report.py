"""Scan commit subjects for issue/ticket label references (e.g. JIRA-123, GH-42)."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

_LABEL_RE = re.compile(r'\b([A-Z][A-Z0-9]+-\d+)\b')


@dataclass
class LabelEntry:
    label: str
    commit_count: int
    authors: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"LabelEntry({self.label!r}, commits={self.commit_count})"


def _extract_labels(subject: str) -> List[str]:
    """Return all uppercase ticket-style labels found in *subject*."""
    return _LABEL_RE.findall(subject)


def build_label_map(commits: Sequence) -> dict[str, LabelEntry]:
    """Build a mapping of label -> LabelEntry from *commits*."""
    entries: dict[str, LabelEntry] = {}
    author_sets: dict[str, set] = defaultdict(set)

    for commit in commits:
        subject = getattr(commit, "subject", "") or ""
        for label in _extract_labels(subject):
            if label not in entries:
                entries[label] = LabelEntry(label=label, commit_count=0)
            entries[label].commit_count += 1
            author = getattr(commit, "author", None)
            if author:
                author_sets[label].add(author)

    for label, entry in entries.items():
        entry.authors = sorted(author_sets[label])

    return entries


def top_n_labels(label_map: dict[str, LabelEntry], n: int = 10) -> List[LabelEntry]:
    """Return the *n* most-referenced labels, descending by commit count."""
    return sorted(label_map.values(), key=lambda e: e.commit_count, reverse=True)[:n]


def format_label_section(label_map: dict[str, LabelEntry], n: int = 10) -> str:
    """Render a plain-text section listing the top referenced ticket labels."""
    top = top_n_labels(label_map, n)
    if not top:
        return ""

    lines = ["Ticket Labels", "-------------"]
    max_count = top[0].commit_count
    bar_width = 20

    for entry in top:
        filled = int(bar_width * entry.commit_count / max_count) if max_count else 0
        bar = "#" * filled + "-" * (bar_width - filled)
        author_str = ", ".join(entry.authors) if entry.authors else "—"
        lines.append(f"{entry.label:<16} [{bar}] {entry.commit_count:>3}  ({author_str})")

    return "\n".join(lines)
