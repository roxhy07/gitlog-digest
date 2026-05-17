"""Detect work-in-progress commits (WIP, draft, fixme, etc.) in the log."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Sequence

_WIP_PATTERNS = re.compile(
    r"\b(wip|draft|do not merge|don'?t merge|dnm|fixme|hack|temp|todo)\b",
    re.IGNORECASE,
)


@dataclass
class WipEntry:
    hash: str
    author: str
    subject: str
    label: str  # the matched keyword / phrase

    def __repr__(self) -> str:  # pragma: no cover
        return f"WipEntry({self.hash!r}, {self.author!r}, label={self.label!r})"


def is_wip_commit(subject: str) -> bool:
    """Return True when *subject* contains a WIP-like keyword."""
    return bool(_WIP_PATTERNS.search(subject))


def _extract_label(subject: str) -> str:
    """Return the first matching WIP keyword found in *subject*, lower-cased."""
    m = _WIP_PATTERNS.search(subject)
    return m.group(0).lower() if m else ""


def build_wip_entries(commits: Sequence) -> List[WipEntry]:
    """Return a list of WipEntry for every commit whose subject looks like WIP."""
    entries: List[WipEntry] = []
    for c in commits:
        subject = getattr(c, "subject", "") or ""
        if is_wip_commit(subject):
            entries.append(
                WipEntry(
                    hash=getattr(c, "hash", ""),
                    author=getattr(c, "author", ""),
                    subject=subject,
                    label=_extract_label(subject),
                )
            )
    return entries


def format_wip_section(entries: List[WipEntry], top_n: int = 10) -> str:
    """Render a plain-text section listing WIP commits."""
    if not entries:
        return ""
    lines = ["WIP / Draft Commits", "=" * 20]
    for e in entries[:top_n]:
        short = e.hash[:7] if len(e.hash) >= 7 else e.hash
        lines.append(f"  [{short}] ({e.label}) {e.subject}  — {e.author}")
    if len(entries) > top_n:
        lines.append(f"  … and {len(entries) - top_n} more")
    return "\n".join(lines)
