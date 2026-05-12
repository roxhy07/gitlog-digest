"""Lightweight git blame helpers — maps files to their top contributors."""

from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FileBlame:
    """Blame summary for a single file."""

    path: str
    line_counts: Dict[str, int] = field(default_factory=dict)  # author -> lines

    @property
    def top_author(self) -> Optional[str]:
        """Return the author with the most lines, or None if empty."""
        if not self.line_counts:
            return None
        return max(self.line_counts, key=lambda a: self.line_counts[a])

    @property
    def total_lines(self) -> int:
        return sum(self.line_counts.values())


def _run_blame(repo: str, filepath: str) -> List[str]:
    """Run git blame --porcelain and return stdout lines."""
    result = subprocess.run(
        ["git", "-C", repo, "blame", "--porcelain", filepath],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def parse_blame_output(lines: List[str]) -> Dict[str, int]:
    """Parse porcelain blame output into {author: line_count}."""
    counts: Counter = Counter()
    for line in lines:
        if line.startswith("author "):
            author = line[len("author "):].strip()
            counts[author] += 1
    return dict(counts)


def blame_file(repo: str, filepath: str) -> FileBlame:
    """Return a FileBlame for *filepath* inside *repo*."""
    lines = _run_blame(repo, filepath)
    counts = parse_blame_output(lines)
    return FileBlame(path=filepath, line_counts=counts)


def blame_files(repo: str, filepaths: List[str]) -> List[FileBlame]:
    """Return FileBlame objects for each path, skipping failures silently."""
    results = []
    for fp in filepaths:
        fb = blame_file(repo, fp)
        if fb.total_lines > 0:
            results.append(fb)
    return results
