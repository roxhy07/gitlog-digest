"""Detect and report co-author relationships from commit trailers."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

CO_AUTHOR_TRAILER = "co-authored-by:"


@dataclass
class CoAuthorPair:
    driver: str
    navigator: str
    commit_count: int = 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"CoAuthorPair({self.driver!r}, {self.navigator!r}, commits={self.commit_count})"


@dataclass
class CoAuthorReport:
    pairs: List[CoAuthorPair] = field(default_factory=list)
    solo_authors: List[str] = field(default_factory=list)


def _extract_coauthors(body: str) -> List[str]:
    """Parse Co-authored-by trailers from a commit body string."""
    names: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(CO_AUTHOR_TRAILER):
            rest = stripped[len(CO_AUTHOR_TRAILER):].strip()
            # Format: "Name <email>" — grab the name part
            name = rest.split("<")[0].strip()
            if name:
                names.append(name)
    return names


def build_coauthor_map(
    commits,
) -> Dict[Tuple[str, str], int]:
    """Return a mapping of (driver, navigator) -> commit count."""
    pair_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    for commit in commits:
        body = getattr(commit, "body", "") or ""
        coauthors = _extract_coauthors(body)
        for coauthor in coauthors:
            key = (commit.author, coauthor)
            pair_counts[key] += 1
    return dict(pair_counts)


def top_pairs(pair_map: Dict[Tuple[str, str], int], n: int = 10) -> List[CoAuthorPair]:
    """Return the top-n co-author pairs sorted by commit count descending."""
    sorted_pairs = sorted(pair_map.items(), key=lambda x: x[1], reverse=True)
    return [
        CoAuthorPair(driver=driver, navigator=nav, commit_count=count)
        for (driver, nav), count in sorted_pairs[:n]
    ]


def format_coauthor_section(pairs: List[CoAuthorPair], top_n: int = 10) -> str:
    """Render a plain-text co-author collaboration section."""
    if not pairs:
        return ""
    lines = ["### Co-author Pairs", ""]
    for pair in pairs[:top_n]:
        lines.append(f"  {pair.driver} + {pair.navigator}: {pair.commit_count} commit(s)")
    lines.append("")
    return "\n".join(lines)
