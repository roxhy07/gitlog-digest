"""Command-line interface for gitlog-digest."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from gitlog_digest.git_parser import fetch_commits, group_by_author
from gitlog_digest.summarizer import WeeklyDigest, build_author_summary
from gitlog_digest.formatter import format_digest


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="gitlog-digest",
        description="Generate a readable weekly summary from git history.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="DATE",
        help="Start date in YYYY-MM-DD format (default: 7 days ago)",
    )
    parser.add_argument(
        "--until",
        default=None,
        metavar="DATE",
        help="End date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write output to a file instead of stdout",
    )
    parser.add_argument(
        "--branch",
        default="HEAD",
        help="Branch or ref to read history from (default: HEAD)",
    )
    return parser.parse_args(argv)


def resolve_dates(since_str, until_str):
    today = datetime.utcnow().date()
    until = datetime.strptime(until_str, "%Y-%m-%d").date() if until_str else today
    since = (
        datetime.strptime(since_str, "%Y-%m-%d").date()
        if since_str
        else until - timedelta(days=7)
    )
    return str(since), str(until)


def main(argv=None):
    args = parse_args(argv)

    repo_path = Path(args.repo).resolve()
    if not (repo_path / ".git").exists():
        print(f"error: '{repo_path}' does not appear to be a git repository.", file=sys.stderr)
        sys.exit(1)

    since, until = resolve_dates(args.since, args.until)

    commits = fetch_commits(str(repo_path), since=since, until=until, branch=args.branch)
    if not commits:
        print("No commits found for the given range.", file=sys.stderr)
        sys.exit(0)

    by_author = group_by_author(commits)
    author_summaries = [build_author_summary(author, author_commits) for author, author_commits in by_author.items()]
    digest = WeeklyDigest(since=since, until=until, authors=author_summaries)
    output = format_digest(digest)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Digest written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
