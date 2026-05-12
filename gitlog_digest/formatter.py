"""Formats a WeeklyDigest into a human-readable text summary."""

from gitlog_digest.summarizer import AuthorSummary, WeeklyDigest

MAX_SUBJECTS = 5
MAX_FILES = 8


def format_author_section(summary: AuthorSummary) -> str:
    lines = []
    lines.append(f"### {summary.author}")
    lines.append(f"  {summary.commit_count} commit(s)")

    subjects = summary.subjects[:MAX_SUBJECTS]
    lines.append("  Highlights:")
    for subject in subjects:
        lines.append(f"    - {subject}")
    if len(summary.subjects) > MAX_SUBJECTS:
        remaining = len(summary.subjects) - MAX_SUBJECTS
        lines.append(f"    ... and {remaining} more")

    unique_files = summary.unique_files()
    if unique_files:
        shown = unique_files[:MAX_FILES]
        lines.append("  Files touched:")
        for f in shown:
            lines.append(f"    · {f}")
        if len(unique_files) > MAX_FILES:
            lines.append(f"    · ... and {len(unique_files) - MAX_FILES} more files")

    return "\n".join(lines)


def format_digest(digest: WeeklyDigest) -> str:
    header_date = (
        f"{digest.week_start.strftime('%b %d')} – {digest.week_end.strftime('%b %d, %Y')}"
    )
    lines = [
        f"# Weekly Git Digest: {header_date}",
        f"  {digest.total_commits} total commit(s) by {digest.total_authors} author(s)",
        "",
    ]

    if not digest.author_summaries:
        lines.append("_No commits found for this period._")
    else:
        for summary in digest.author_summaries:
            lines.append(format_author_section(summary))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
