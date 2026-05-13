"""Generate a summary report of git tags found within a commit range."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TagEntry:
    name: str
    sha: str
    subject: str
    date: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"TagEntry({self.name!r}, {self.sha[:7]})"


def _run_git(args: List[str], repo: str = ".") -> str:
    result = subprocess.run(
        ["git", "-C", repo] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def fetch_tags_in_range(
    repo: str = ".",
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> List[TagEntry]:
    """Return tags whose tagged commit falls within [since, until]."""
    fmt = "%(refname:short)%09%(objectname:short)%09%(subject)%09%(creatordate:short)"
    raw = _run_git(["tag", "--sort=-creatordate", f"--format={fmt}"], repo=repo)
    if not raw:
        return []

    entries: List[TagEntry] = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        name, sha, subject, date = parts[0], parts[1], parts[2], parts[3]
        if since and date < since:
            continue
        if until and date > until:
            continue
        entries.append(TagEntry(name=name, sha=sha, subject=subject, date=date))

    return entries


def format_tag_report(tags: List[TagEntry], header_level: int = 2) -> str:
    """Render a markdown section listing tags."""
    if not tags:
        return ""

    hashes = "#" * header_level
    lines = [f"{hashes} Tags ({len(tags)})", ""]
    for tag in tags:
        lines.append(f"- **{tag.name}** `{tag.sha}` — {tag.subject} _{tag.date}_")
    lines.append("")
    return "\n".join(lines)
