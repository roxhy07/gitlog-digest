"""Analyse conventional-commit scopes from commit subjects.

Extracts the scope portion from messages like ``feat(auth): add login``
and tallies how often each scope appears across the commit range.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

_SCOPE_RE = re.compile(r"^[a-zA-Z]+\(([^)]+)\)")


def _extract_scope(subject: str) -> Optional[str]:
    """Return the scope string from a conventional-commit subject, or None."""
    m = _SCOPE_RE.match(subject.strip())
    return m.group(1).lower() if m else None


@dataclass
class ScopeEntry:
    scope: str
    count: int = 0
    authors: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScopeEntry(scope={self.scope!r}, count={self.count})"


def build_scope_map(commits: Sequence) -> dict[str, ScopeEntry]:
    """Return a mapping of scope -> ScopeEntry for *commits*."""
    result: dict[str, ScopeEntry] = {}
    for commit in commits:
        scope = _extract_scope(getattr(commit, "subject", "") or "")
        if scope is None:
            continue
        if scope not in result:
            result[scope] = ScopeEntry(scope=scope)
        entry = result[scope]
        entry.count += 1
        author = getattr(commit, "author", None)
        if author and author not in entry.authors:
            entry.authors.append(author)
    return result


def top_n_scopes(scope_map: dict[str, ScopeEntry], n: int = 10) -> List[ScopeEntry]:
    """Return up to *n* ScopeEntry objects sorted by count descending."""
    return sorted(scope_map.values(), key=lambda e: e.count, reverse=True)[:n]


def _scope_bar(count: int, max_count: int, width: int = 20) -> str:
    if max_count == 0:
        return " " * width
    filled = round(width * count / max_count)
    return "█" * filled + "░" * (width - filled)


def format_scope_section(entries: List[ScopeEntry]) -> str:
    """Render a plain-text table of scope activity."""
    if not entries:
        return ""
    max_count = max(e.count for e in entries)
    lines = ["Scope Breakdown", "---------------"]
    for e in entries:
        bar = _scope_bar(e.count, max_count)
        lines.append(f"  {e.scope:<20} {bar} {e.count:>4} commit(s)")
    return "\n".join(lines)
