"""Parse raw git log output into structured commit data."""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


GIT_LOG_FORMAT = "%H|%an|%ae|%ad|%s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


@dataclass
class Commit:
    hash: str
    author_name: str
    author_email: str
    date: datetime
    subject: str
    files_changed: list[str] = field(default_factory=list)

    @property
    def short_hash(self) -> str:
        return self.hash[:7]

    def __repr__(self) -> str:
        return f"Commit({self.short_hash}, '{self.subject[:40]}...')"


def fetch_commits(
    repo_path: str = ".",
    since: Optional[str] = None,
    until: Optional[str] = None,
    branch: str = "HEAD",
) -> list[Commit]:
    """Run git log and return a list of Commit objects."""
    cmd = [
        "git", "-C", repo_path,
        "log", branch,
        f"--format={GIT_LOG_FORMAT}",
        "--date=format:%Y-%m-%d %H:%M:%S %z",
    ]
    if since:
        cmd += [f"--since={since}"]
    if until:
        cmd += [f"--until={until}"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    commits = []
    for line in result.stdout.strip().splitlines():
        if not line:
            continue
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue
        hash_, author_name, author_email, date_str, subject = parts
        try:
            date = datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            continue
        commits.append(Commit(
            hash=hash_,
            author_name=author_name,
            author_email=author_email,
            date=date,
            subject=subject,
        ))
    return commits


def group_by_author(commits: list[Commit]) -> dict[str, list[Commit]]:
    """Group commits by author name."""
    groups: dict[str, list[Commit]] = {}
    for commit in commits:
        groups.setdefault(commit.author_name, []).append(commit)
    return groups
