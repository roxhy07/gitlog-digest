"""Detect and format milestone commits (first commit, Nth commit, etc.)."""

from dataclasses import dataclass, field
from typing import List, Optional

from gitlog_digest.git_parser import Commit

DEFAULT_MILESTONES = {1, 10, 50, 100, 250, 500, 1000}


@dataclass
class Milestone:
    number: int
    commit: Commit
    label: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Milestone #{self.number} {self.commit.short_hash()}>"


def detect_milestones(
    commits: List[Commit],
    thresholds: Optional[set] = None,
) -> List[Milestone]:
    """Return milestones hit within *commits* (ordered oldest-first).

    Commits are assumed to arrive newest-first (standard git log order);
    we reverse internally so numbering starts at 1 for the very first commit.
    """
    if thresholds is None:
        thresholds = DEFAULT_MILESTONES

    ordered = list(reversed(commits))
    milestones: List[Milestone] = []

    for idx, commit in enumerate(ordered, start=1):
        if idx in thresholds:
            label = _milestone_label(idx)
            milestones.append(Milestone(number=idx, commit=commit, label=label))

    return milestones


def _milestone_label(n: int) -> str:
    if n == 1:
        return "First commit"
    return f"Commit #{n:,}"


def format_milestone_report(milestones: List[Milestone], markdown: bool = True) -> str:
    """Render a short milestone section suitable for embedding in a digest."""
    if not milestones:
        return ""

    lines: List[str] = []
    if markdown:
        lines.append("## Milestones")
    else:
        lines.append("Milestones")
        lines.append("-" * 10)

    for m in milestones:
        author = m.commit.author
        subject = m.commit.subject[:60]
        if markdown:
            lines.append(f"- **{m.label}** — `{m.commit.short_hash()}` {subject} _{author}_")
        else:
            lines.append(f"  {m.label}: [{m.commit.short_hash()}] {subject} ({author})")

    return "\n".join(lines)
