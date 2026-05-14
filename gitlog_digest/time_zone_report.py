"""Analyse commit timestamps to surface per-author time-zone patterns."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


@dataclass
class TimeZoneEntry:
    author: str
    offsets: List[str] = field(default_factory=list)  # e.g. ["+0200", "+0200", "-0500"]

    def __repr__(self) -> str:  # pragma: no cover
        return f"TimeZoneEntry(author={self.author!r}, primary={self.primary_offset!r})"

    @property
    def primary_offset(self) -> Optional[str]:
        """Most frequently used UTC offset, or None if no data."""
        if not self.offsets:
            return None
        return max(set(self.offsets), key=self.offsets.count)

    @property
    def unique_offsets(self) -> List[str]:
        seen: list = []
        for o in self.offsets:
            if o not in seen:
                seen.append(o)
        return seen


def build_time_zone_map(commits: Sequence) -> Dict[str, TimeZoneEntry]:
    """Return a mapping of author -> TimeZoneEntry from *commits*.

    Each commit is expected to expose:
      - ``author``  (str)
      - ``date``    (str) in git's ISO-strict format, e.g. "2024-03-15T09:42:00+02:00"
    """
    entries: Dict[str, TimeZoneEntry] = {}
    for commit in commits:
        author = commit.author
        if author not in entries:
            entries[author] = TimeZoneEntry(author=author)
        offset = _extract_offset(commit.date)
        if offset:
            entries[author].offsets.append(offset)
    return entries


def _extract_offset(date_str: str) -> Optional[str]:
    """Pull the UTC offset from an ISO-8601 date string.

    Handles both ``+HH:MM`` / ``-HH:MM`` and ``+HHMM`` / ``-HHMM`` forms.
    Returns a normalised ``+HHMM`` string, or *None* on failure.
    """
    if not date_str:
        return None
    for sep in ("T", " "):
        if sep in date_str:
            time_part = date_str.split(sep, 1)[1]
            for sign in ("+", "-"):
                idx = time_part.rfind(sign)
                if idx != -1:
                    raw = time_part[idx:]          # e.g. "+02:00" or "+0200"
                    raw = raw.replace(":", "")     # normalise to "+0200"
                    if len(raw) == 5:              # sign + 4 digits
                        return raw
    return None


def format_time_zone_section(entries: Dict[str, TimeZoneEntry], top_n: int = 10) -> str:
    """Render a plain-text section listing each author's primary time zone."""
    if not entries:
        return ""
    lines = ["## Time Zone Overview", ""]
    sorted_entries = sorted(entries.values(), key=lambda e: e.author.lower())
    for entry in sorted_entries[:top_n]:
        offset = entry.primary_offset or "unknown"
        zones = ", ".join(entry.unique_offsets) if len(entry.unique_offsets) > 1 else ""
        extra = f"  (also seen: {zones})" if zones else ""
        lines.append(f"  {entry.author}: {offset}{extra}")
    lines.append("")
    return "\n".join(lines)
