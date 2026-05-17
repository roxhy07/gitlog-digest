"""Ribbon (award/badge) report: assigns achievement badges to contributors."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class RibbonEntry:
    author: str
    badges: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RibbonEntry(author={self.author!r}, badges={self.badges!r})"


def _assign_badges(author: str, commit_count: int, files_changed: int, net_lines: int) -> List[str]:
    badges: List[str] = []
    if commit_count >= 50:
        badges.append("Prolific Committer")
    elif commit_count >= 10:
        badges.append("Active Contributor")
    if files_changed >= 100:
        badges.append("File Wrangler")
    if net_lines >= 1000:
        badges.append("Code Grower")
    elif net_lines <= -500:
        badges.append("Code Trimmer")
    if commit_count == 1:
        badges.append("First Step")
    if not badges:
        badges.append("Participant")
    return badges


def build_ribbon_map(commits: Sequence) -> dict[str, RibbonEntry]:
    """Build a map of author -> RibbonEntry from a sequence of Commit objects."""
    from collections import defaultdict

    counts: dict[str, int] = defaultdict(int)
    files: dict[str, set] = defaultdict(set)
    net: dict[str, int] = defaultdict(int)

    for c in commits:
        counts[c.author] += 1
        for f in getattr(c, "files_changed", []):
            files[c.author].add(f)
        ds = getattr(c, "diff_stats", None)
        if ds is not None:
            net[c.author] += getattr(ds, "additions", 0) - getattr(ds, "deletions", 0)

    result: dict[str, RibbonEntry] = {}
    for author in counts:
        badges = _assign_badges(author, counts[author], len(files[author]), net[author])
        result[author] = RibbonEntry(author=author, badges=badges)
    return result


def format_ribbon_section(ribbon_map: dict[str, RibbonEntry], top_n: int = 10) -> str:
    if not ribbon_map:
        return ""
    lines = ["### 🎖 Contributor Ribbons", ""]
    entries = sorted(ribbon_map.values(), key=lambda e: len(e.badges), reverse=True)
    for entry in entries[:top_n]:
        badge_str = "  ".join(f"[{b}]" for b in entry.badges)
        lines.append(f"- **{entry.author}**: {badge_str}")
    return "\n".join(lines)
