"""Detect and summarise fixup / squash commits in the git log."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

_FIXUP_RE = re.compile(
    r"^(fixup!|squash!|fix up|amend:|wip:?\s|\[wip\])",
    re.IGNORECASE,
)


@dataclass
class FixupEntry:
    author: str
    hash: str
    subject: str
    kind: str  # 'fixup', 'squash', or 'wip'

    def __repr__(self) -> str:  # pragma: no cover
        return f"FixupEntry({self.author!r}, {self.kind!r}, {self.subject!r})"


def is_fixup_commit(subject: str) -> bool:
    """Return True when the subject looks like a fixup / squash / WIP commit."""
    return bool(_FIXUP_RE.match(subject.strip()))


def _classify(subject: str) -> str:
    low = subject.strip().lower()
    if low.startswith("squash!"):
        return "squash"
    if low.startswith(("wip", "[wip]")):
        return "wip"
    return "fixup"


def build_fixup_entries(commits: Sequence) -> List[FixupEntry]:
    """Return a FixupEntry for every commit whose subject matches."""
    entries: List[FixupEntry] = []
    for c in commits:
        subject = getattr(c, "subject", "") or ""
        if is_fixup_commit(subject):
            entries.append(
                FixupEntry(
                    author=getattr(c, "author", "unknown"),
                    hash=getattr(c, "hash", ""),
                    subject=subject,
                    kind=_classify(subject),
                )
            )
    return entries


def format_fixup_section(entries: List[FixupEntry], top_n: int = 10) -> str:
    """Render a plain-text section listing fixup commits."""
    if not entries:
        return ""
    lines = ["Fixup / WIP commits:", ""]
    for e in entries[:top_n]:
        short = e.hash[:7] if e.hash else "?"
        lines.append(f"  [{e.kind:6s}] {short}  {e.author}: {e.subject}")
    if len(entries) > top_n:
        lines.append(f"  … and {len(entries) - top_n} more")
    return "\n".join(lines)
