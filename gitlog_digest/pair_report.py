"""Detect co-committing pairs — authors who frequently touch the same files."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Sequence


@dataclass
class PairEntry:
    author_a: str
    author_b: str
    shared_files: int
    commit_overlap: int

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PairEntry({self.author_a!r}, {self.author_b!r}, "
            f"files={self.shared_files}, commits={self.commit_overlap})"
        )


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def build_pair_map(commits: Sequence) -> Dict[tuple, PairEntry]:
    """Return a mapping of author-pair -> PairEntry."""
    # file -> set of authors who touched it
    file_authors: Dict[str, set] = defaultdict(set)
    # (author_a, author_b) -> set of shared files
    pair_files: Dict[tuple, set] = defaultdict(set)
    # (author_a, author_b) -> commit overlap count
    pair_commits: Dict[tuple, int] = defaultdict(int)

    for commit in commits:
        files = getattr(commit, "files_changed", []) or []
        author = commit.author
        for f in files:
            for other in file_authors[f]:
                key = _pair_key(author, other)
                pair_files[key].add(f)
            file_authors[f].add(author)

    # count commit overlaps: commits where >= 2 known paired authors appear
    author_commits: Dict[str, set] = defaultdict(set)
    for commit in commits:
        author_commits[commit.author].add(commit.hash)

    all_authors = list(author_commits.keys())
    for a, b in combinations(all_authors, 2):
        key = _pair_key(a, b)
        if key in pair_files:
            overlap = len(author_commits[a] & author_commits[b])
            pair_commits[key] = overlap

    result: Dict[tuple, PairEntry] = {}
    for key, files in pair_files.items():
        result[key] = PairEntry(
            author_a=key[0],
            author_b=key[1],
            shared_files=len(files),
            commit_overlap=pair_commits.get(key, 0),
        )
    return result


def top_pairs(pair_map: Dict[tuple, PairEntry], n: int = 5) -> List[PairEntry]:
    return sorted(pair_map.values(), key=lambda e: e.shared_files, reverse=True)[:n]


def format_pair_section(entries: List[PairEntry], bar_width: int = 20) -> str:
    if not entries:
        return ""
    max_files = max(e.shared_files for e in entries) or 1
    lines = ["### Collaborating Pairs", ""]
    for e in entries:
        filled = round(e.shared_files / max_files * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        lines.append(
            f"  {e.author_a} & {e.author_b}: [{bar}] "
            f"{e.shared_files} shared file(s), {e.commit_overlap} commit overlap"
        )
    return "\n".join(lines)
