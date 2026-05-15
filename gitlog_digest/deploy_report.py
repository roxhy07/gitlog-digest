"""Detect and summarise deployment-related commits."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Sequence

_DEPLOY_PATTERNS = [
    re.compile(r"\bdeploy\b", re.IGNORECASE),
    re.compile(r"\brelease\b", re.IGNORECASE),
    re.compile(r"\bship\b", re.IGNORECASE),
    re.compile(r"\brollout\b", re.IGNORECASE),
    re.compile(r"\bpublish\b", re.IGNORECASE),
]


@dataclass
class DeployEntry:
    author: str
    hash: str
    subject: str
    timestamp: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"DeployEntry({self.hash[:7]} by {self.author!r}: {self.subject!r})"


def is_deploy_commit(subject: str) -> bool:
    """Return True if *subject* matches any deployment keyword."""
    return any(p.search(subject) for p in _DEPLOY_PATTERNS)


def build_deploy_entries(commits: Sequence) -> List[DeployEntry]:
    """Return a list of DeployEntry objects for all deploy-like commits."""
    entries: List[DeployEntry] = []
    for c in commits:
        if is_deploy_commit(getattr(c, "subject", "")):
            entries.append(
                DeployEntry(
                    author=c.author,
                    hash=c.hash,
                    subject=c.subject,
                    timestamp=getattr(c, "timestamp", ""),
                )
            )
    return entries


def format_deploy_section(entries: List[DeployEntry], top_n: int = 10) -> str:
    """Render a plain-text section listing recent deploy commits."""
    if not entries:
        return ""
    lines = ["### Deployments & Releases", ""]
    for e in entries[:top_n]:
        ts = f"  ({e.timestamp})" if e.timestamp else ""
        lines.append(f"  {e.hash[:7]}  {e.subject}  — {e.author}{ts}")
    lines.append("")
    return "\n".join(lines)
