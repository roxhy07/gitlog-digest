"""Commit filtering utilities driven by DigestConfig."""

from __future__ import annotations

import fnmatch
from typing import Iterable

from gitlog_digest.git_parser import Commit
from gitlog_digest.config import DigestConfig


def _matches_any_pattern(subject: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(subject, p) for p in patterns)


def filter_commits(
    commits: Iterable[Commit],
    config: DigestConfig,
) -> list[Commit]:
    """Return commits that pass author and subject-pattern filters."""
    excluded_authors = {a.lower() for a in config.exclude_authors}
    result: list[Commit] = []
    for commit in commits:
        if commit.author.lower() in excluded_authors:
            continue
        if config.exclude_patterns and _matches_any_pattern(
            commit.subject, config.exclude_patterns
        ):
            continue
        result.append(commit)
    return result


def truncate_subjects(
    commits: Iterable[Commit],
    max_length: int,
) -> list[Commit]:
    """Return new Commit objects with subjects capped at max_length."""
    out: list[Commit] = []
    for c in commits:
        if len(c.subject) > max_length:
            new_subject = c.subject[: max_length - 1] + "…"
            out.append(
                Commit(
                    hash=c.hash,
                    author=c.author,
                    date=c.date,
                    subject=new_subject,
                    files_changed=c.files_changed,
                )
            )
        else:
            out.append(c)
    return out


def apply_filters(commits: Iterable[Commit], config: DigestConfig) -> list[Commit]:
    """Convenience: filter then truncate subjects."""
    filtered = filter_commits(commits, config)
    return truncate_subjects(filtered, config.max_subject_length)
