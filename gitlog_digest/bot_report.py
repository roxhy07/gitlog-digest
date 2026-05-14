"""Detect and report on bot/automated commits in the git history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

# Common patterns that indicate a bot or automated author
_BOT_PATTERNS = (
    "[bot]",
    "-bot",
    "bot-",
    "automation",
    "ci-",
    "-ci",
    "dependabot",
    "renovate",
    "github-actions",
    "snyk-bot",
)


@dataclass
class BotEntry:
    author: str
    commit_count: int
    subjects: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"BotEntry(author={self.author!r}, commits={self.commit_count})"


def is_bot_author(author: str) -> bool:
    """Return True when *author* looks like a bot or automated account."""
    lower = author.lower()
    return any(pat in lower for pat in _BOT_PATTERNS)


def build_bot_map(commits: Sequence) -> dict[str, BotEntry]:
    """Group bot commits by author name and return a mapping."""
    entries: dict[str, BotEntry] = {}
    for commit in commits:
        if not is_bot_author(commit.author):
            continue
        if commit.author not in entries:
            entries[commit.author] = BotEntry(author=commit.author, commit_count=0)
        entry = entries[commit.author]
        entry.commit_count += 1
        entry.subjects.append(commit.subject)
    return entries


def top_bots(entries: dict[str, BotEntry], n: int = 5) -> List[BotEntry]:
    """Return up to *n* bot entries sorted by commit count descending."""
    return sorted(entries.values(), key=lambda e: e.commit_count, reverse=True)[:n]


def format_bot_section(entries: dict[str, BotEntry], n: int = 5) -> str:
    """Render a plain-text summary of the top bot contributors."""
    bots = top_bots(entries, n)
    if not bots:
        return ""
    lines = ["Bot / Automated Commits", "-" * 24]
    for entry in bots:
        lines.append(f"  {entry.author}: {entry.commit_count} commit(s)")
        for subj in entry.subjects[:3]:
            lines.append(f"    - {subj}")
        if len(entry.subjects) > 3:
            lines.append(f"    ... and {len(entry.subjects) - 3} more")
    return "\n".join(lines)
