"""Detect and summarise revert commits in the git log."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Sequence

_REVERT_RE = re.compile(r'^revert\b', re.IGNORECASE)
_SHA_RE = re.compile(r'[0-9a-f]{7,40}', re.IGNORECASE)


@dataclass
class RevertEntry:
    author: str
    subject: str
    hash: str
    reverted_hash: str | None = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"RevertEntry(author={self.author!r}, hash={self.hash!r})"


def is_revert_commit(subject: str) -> bool:
    """Return True when the subject line looks like a revert commit."""
    return bool(_REVERT_RE.match(subject.strip()))


def _extract_reverted_hash(body: str) -> str | None:
    """Try to pull the original commit SHA out of the revert body text."""
    if not body:
        return None
    match = _SHA_RE.search(body)
    return match.group(0) if match else None


def build_revert_entries(commits: Sequence) -> List[RevertEntry]:
    """Return a list of RevertEntry objects for every revert commit found."""
    entries: List[RevertEntry] = []
    for commit in commits:
        if not is_revert_commit(getattr(commit, 'subject', '')):
            continue
        body = getattr(commit, 'body', '') or ''
        entries.append(
            RevertEntry(
                author=commit.author,
                subject=commit.subject,
                hash=commit.hash,
                reverted_hash=_extract_reverted_hash(body),
            )
        )
    return entries


def format_revert_section(entries: List[RevertEntry], top_n: int = 10) -> str:
    """Render a plain-text summary of the top revert commits."""
    if not entries:
        return ''
    lines = ['Revert Commits', '-' * 14]
    for entry in entries[:top_n]:
        sha_hint = f" (reverts {entry.reverted_hash})" if entry.reverted_hash else ''
        lines.append(f"  {entry.hash[:7]}  {entry.author}: {entry.subject}{sha_hint}")
    lines.append(f"  Total reverts: {len(entries)}")
    return '\n'.join(lines)
