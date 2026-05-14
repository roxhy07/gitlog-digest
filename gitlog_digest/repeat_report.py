"""Detect files that appear repeatedly across commits (hot files)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class RepeatEntry:
    filepath: str
    commit_count: int
    authors: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RepeatEntry({self.filepath!r}, commits={self.commit_count})"


def build_repeat_map(commits) -> dict[str, RepeatEntry]:
    """Return a mapping of filepath -> RepeatEntry across all commits."""
    file_commits: dict[str, list[str]] = {}

    for commit in commits:
        for filepath in commit.files_changed:
            if filepath not in file_commits:
                file_commits[filepath] = []
            file_commits[filepath].append(commit.author)

    result: dict[str, RepeatEntry] = {}
    for filepath, authors in file_commits.items():
        unique_authors = list(dict.fromkeys(authors))  # preserve first-seen order
        result[filepath] = RepeatEntry(
            filepath=filepath,
            commit_count=len(authors),
            authors=unique_authors,
        )
    return result


def top_repeated_files(repeat_map: dict[str, RepeatEntry], n: int = 10) -> List[RepeatEntry]:
    """Return the top-n files sorted by commit count descending."""
    return sorted(repeat_map.values(), key=lambda e: e.commit_count, reverse=True)[:n]


def _repeat_bar(count: int, max_count: int, width: int = 20) -> str:
    if max_count == 0:
        return " " * width
    filled = round(width * count / max_count)
    return "#" * filled + "-" * (width - filled)


def format_repeat_section(entries: Sequence[RepeatEntry], width: int = 20) -> str:
    """Render a plain-text table of repeatedly touched files."""
    if not entries:
        return ""

    max_count = max(e.commit_count for e in entries)
    lines = ["Hot Files (most frequently changed):", ""]
    for entry in entries:
        bar = _repeat_bar(entry.commit_count, max_count, width)
        authors_str = ", ".join(entry.authors[:3])
        if len(entry.authors) > 3:
            authors_str += f" +{len(entry.authors) - 3}"
        lines.append(f"  [{bar}] {entry.commit_count:>4}x  {entry.filepath}")
        lines.append(f"           authors: {authors_str}")
    return "\n".join(lines)
