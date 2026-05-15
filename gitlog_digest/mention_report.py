"""Scan commit messages for @mentions and tally how often each handle appears."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Sequence

_MENTION_RE = re.compile(r"@([A-Za-z0-9_.-]+)")


@dataclass
class MentionEntry:
    handle: str
    count: int
    commit_hashes: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"MentionEntry(handle={self.handle!r}, count={self.count})"


def _extract_mentions(text: str) -> List[str]:
    """Return all @-handles found in *text*, lower-cased."""
    return [m.lower() for m in _MENTION_RE.findall(text)]


def build_mention_map(commits: Sequence) -> dict[str, MentionEntry]:
    """Return a mapping of handle -> MentionEntry for every commit."""
    entries: dict[str, MentionEntry] = {}
    for commit in commits:
        subject = getattr(commit, "subject", "") or ""
        body = getattr(commit, "body", "") or ""
        handles = _extract_mentions(f"{subject} {body}")
        seen_in_commit: set[str] = set()
        for handle in handles:
            if handle not in entries:
                entries[handle] = MentionEntry(handle=handle, count=0)
            if handle not in seen_in_commit:
                entries[handle].count += 1
                seen_in_commit.add(handle)
            entries[handle].commit_hashes.append(commit.hash)
    return entries


def top_n_mentions(mention_map: dict[str, MentionEntry], n: int = 10) -> List[MentionEntry]:
    """Return the top *n* handles sorted by descending count."""
    return sorted(mention_map.values(), key=lambda e: e.count, reverse=True)[:n]


def _mention_bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return " " * width
    filled = round(value / max_value * width)
    return "#" * filled + "-" * (width - filled)


def format_mention_section(entries: List[MentionEntry], width: int = 20) -> str:
    """Render a plain-text table of mention counts."""
    if not entries:
        return ""
    max_count = max(e.count for e in entries)
    lines = ["@Mentions", "-" * 40]
    for entry in entries:
        bar = _mention_bar(entry.count, max_count, width)
        lines.append(f"  @{entry.handle:<20} {bar}  {entry.count}")
    return "\n".join(lines)
