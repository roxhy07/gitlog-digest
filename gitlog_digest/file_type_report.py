"""Groups commits and changed files by file extension for a quick language/type breakdown."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


@dataclass
class FileTypeEntry:
    extension: str
    file_count: int
    commit_count: int
    authors: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FileTypeEntry(ext={self.extension!r}, files={self.file_count}, "
            f"commits={self.commit_count})"
        )


def _ext(filename: str) -> str:
    """Return normalised extension, e.g. '.py', or '<no ext>' for files without one."""
    suffix = Path(filename).suffix.lower()
    return suffix if suffix else "<no ext>"


def build_file_type_map(commits) -> Dict[str, FileTypeEntry]:
    """Aggregate per-extension stats across all commits."""
    files_by_ext: Dict[str, set] = defaultdict(set)
    commits_by_ext: Dict[str, set] = defaultdict(set)
    authors_by_ext: Dict[str, set] = defaultdict(set)

    for commit in commits:
        for filename in getattr(commit, "files_changed", []):
            ext = _ext(filename)
            files_by_ext[ext].add(filename)
            commits_by_ext[ext].add(commit.hash)
            authors_by_ext[ext].add(commit.author)

    result: Dict[str, FileTypeEntry] = {}
    for ext in files_by_ext:
        result[ext] = FileTypeEntry(
            extension=ext,
            file_count=len(files_by_ext[ext]),
            commit_count=len(commits_by_ext[ext]),
            authors=sorted(authors_by_ext[ext]),
        )
    return result


def top_n_types(mapping: Dict[str, FileTypeEntry], n: int = 10) -> List[FileTypeEntry]:
    """Return the top-n entries sorted by file_count descending."""
    return sorted(mapping.values(), key=lambda e: e.file_count, reverse=True)[:n]


def format_file_type_section(entries: List[FileTypeEntry], bar_width: int = 20) -> str:
    """Render a plain-text table of file-type breakdown."""
    if not entries:
        return ""

    max_files = max(e.file_count for e in entries) or 1
    lines = ["File-type breakdown:", ""]
    for entry in entries:
        bar_len = round(entry.file_count / max_files * bar_width)
        bar = "#" * bar_len + "-" * (bar_width - bar_len)
        lines.append(
            f"  {entry.extension:<12} [{bar}] {entry.file_count:>4} file(s)  "
            f"{entry.commit_count} commit(s)"
        )
    return "\n".join(lines)


def author_extension_matrix(mapping: Dict[str, FileTypeEntry]) -> Dict[str, List[str]]:
    """Return a mapping of author -> list of extensions they touched.

    Useful for a quick overview of which languages each contributor worked in.
    """
    matrix: Dict[str, List[str]] = defaultdict(list)
    for ext, entry in sorted(mapping.items()):
        for author in entry.authors:
            matrix[author].append(ext)
    return dict(matrix)
