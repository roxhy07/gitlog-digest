"""Generates weekly digest summaries from grouped git commits."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

from gitlog_digest.git_parser import Commit, group_by_author


@dataclass
class AuthorSummary:
    author: str
    commit_count: int
    files_changed: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)

    def unique_files(self) -> List[str]:
        return sorted(set(self.files_changed))


@dataclass
class WeeklyDigest:
    week_start: date
    week_end: date
    author_summaries: List[AuthorSummary] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        return sum(s.commit_count for s in self.author_summaries)

    @property
    def total_authors(self) -> int:
        return len(self.author_summaries)


def build_author_summary(author: str, commits: List[Commit]) -> AuthorSummary:
    all_files: List[str] = []
    subjects: List[str] = []

    for commit in commits:
        all_files.extend(commit.files_changed)
        subjects.append(commit.subject)

    return AuthorSummary(
        author=author,
        commit_count=len(commits),
        files_changed=all_files,
        subjects=subjects,
    )


def build_digest(
    commits: List[Commit],
    week_start: Optional[date] = None,
) -> WeeklyDigest:
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)
    grouped = group_by_author(commits)

    summaries = [
        build_author_summary(author, author_commits)
        for author, author_commits in sorted(grouped.items())
    ]

    return WeeklyDigest(
        week_start=week_start,
        week_end=week_end,
        author_summaries=summaries,
    )
