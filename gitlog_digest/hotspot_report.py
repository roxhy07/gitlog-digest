"""Identifies files that are both frequently changed and touched by many authors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class HotspotEntry:
    filepath: str
    commit_count: int
    author_count: int
    authors: List[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        """Higher score = bigger hotspot (commit volume * author spread)."""
        return self.commit_count * self.author_count

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"HotspotEntry({self.filepath!r}, commits={self.commit_count}, "
            f"authors={self.author_count}, score={self.score:.1f})"
        )


def build_hotspot_map(commits) -> Dict[str, HotspotEntry]:
    """Build a map of filepath -> HotspotEntry from an iterable of commits."""
    file_commits: Dict[str, int] = {}
    file_authors: Dict[str, set] = {}

    for commit in commits:
        files = getattr(commit, "files_changed", []) or []
        author = getattr(commit, "author", "") or ""
        for filepath in files:
            if filepath not in file_commits:
                file_commits[filepath] = 0
                file_authors[filepath] = set()
            file_commits[filepath] += 1
            if author:
                file_authors[filepath].add(author)

    result: Dict[str, HotspotEntry] = {}
    for filepath, count in file_commits.items():
        authors_sorted = sorted(file_authors[filepath])
        result[filepath] = HotspotEntry(
            filepath=filepath,
            commit_count=count,
            author_count=len(authors_sorted),
            authors=authors_sorted,
        )
    return result


def top_hotspots(hotspot_map: Dict[str, HotspotEntry], n: int = 10) -> List[HotspotEntry]:
    """Return the top-n hotspot entries sorted by score descending."""
    entries = sorted(hotspot_map.values(), key=lambda e: (e.score, e.commit_count), reverse=True)
    return entries[:n]


def _hotspot_bar(score: float, max_score: float, width: int = 20) -> str:
    if max_score <= 0:
        return " " * width
    filled = round((score / max_score) * width)
    return "█" * filled + "░" * (width - filled)


def format_hotspot_section(entries: List[HotspotEntry]) -> str:
    """Render a plain-text hotspot section."""
    if not entries:
        return ""
    max_score = max(e.score for e in entries) if entries else 1.0
    lines = ["## Hotspots\n"]
    for entry in entries:
        bar = _hotspot_bar(entry.score, max_score)
        lines.append(
            f"  {bar} {entry.filepath} "
            f"({entry.commit_count} commits, {entry.author_count} authors)"
        )
    return "\n".join(lines)
