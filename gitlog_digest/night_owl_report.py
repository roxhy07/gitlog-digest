"""Report identifying commits made outside normal working hours (before 9am or after 6pm)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Sequence

LATE_NIGHT_START = 22   # 10pm
EARLY_MORNING_END = 6   # 6am
AFTER_HOURS_START = 18  # 6pm
WORK_START = 9          # 9am


@dataclass
class NightOwlEntry:
    author: str
    commit_count: int = 0
    late_night_count: int = 0   # 10pm – 6am
    after_hours_count: int = 0  # 6pm – 10pm
    early_bird_count: int = 0   # before 9am
    sample_times: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NightOwlEntry(author={self.author!r}, "
            f"commits={self.commit_count}, "
            f"late_night={self.late_night_count}, "
            f"after_hours={self.after_hours_count}, "
            f"early_bird={self.early_bird_count})"
        )

    @property
    def off_hours_total(self) -> int:
        return self.late_night_count + self.after_hours_count + self.early_bird_count


def _classify_hour(hour: int) -> str:
    """Return a string label for the given hour."""
    if hour >= LATE_NIGHT_START or hour < EARLY_MORNING_END:
        return "late_night"
    if hour < WORK_START:
        return "early_bird"
    if hour >= AFTER_HOURS_START:
        return "after_hours"
    return "working_hours"


def build_night_owl_map(commits: Sequence) -> dict[str, NightOwlEntry]:
    """Build a mapping of author -> NightOwlEntry from commit list."""
    result: dict[str, NightOwlEntry] = {}
    for commit in commits:
        author = commit.author
        if author not in result:
            result[author] = NightOwlEntry(author=author)
        entry = result[author]
        entry.commit_count += 1
        try:
            dt = datetime.fromisoformat(commit.date)
        except (ValueError, AttributeError):
            continue
        hour = dt.hour
        label = _classify_hour(hour)
        if label == "late_night":
            entry.late_night_count += 1
        elif label == "early_bird":
            entry.early_bird_count += 1
        elif label == "after_hours":
            entry.after_hours_count += 1
        if label != "working_hours" and len(entry.sample_times) < 3:
            entry.sample_times.append(dt.strftime("%H:%M"))
    return result


def top_night_owls(mapping: dict[str, NightOwlEntry], n: int = 5) -> List[NightOwlEntry]:
    """Return the top n authors sorted by off-hours commit count."""
    entries = [e for e in mapping.values() if e.off_hours_total > 0]
    return sorted(entries, key=lambda e: e.off_hours_total, reverse=True)[:n]


def format_night_owl_section(mapping: dict[str, NightOwlEntry], n: int = 5) -> str:
    """Return a plain-text summary of night-owl activity."""
    top = top_night_owls(mapping, n)
    if not top:
        return ""
    lines = ["Night Owl Activity", "=================="]
    for entry in top:
        bar = "*" * min(entry.off_hours_total, 20)
        samples = ", ".join(entry.sample_times) if entry.sample_times else "—"
        lines.append(
            f"  {entry.author:<20} {bar:<20} "
            f"off-hours={entry.off_hours_total} "
            f"(late={entry.late_night_count}, "
            f"after={entry.after_hours_count}, "
            f"early={entry.early_bird_count}) "
            f"sample times: {samples}"
        )
    return "\n".join(lines)
