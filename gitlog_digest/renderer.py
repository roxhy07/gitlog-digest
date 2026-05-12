"""Renders WeeklyDigest summaries to various output formats (markdown, plain text)."""

from __future__ import annotations

from typing import Literal

from gitlog_digest.summarizer import WeeklyDigest

OutputFormat = Literal["markdown", "plain"]


def _md_header(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def render_markdown(digest: WeeklyDigest) -> str:
    lines: list[str] = []
    lines.append(_md_header(1, f"Weekly Digest: {digest.since} – {digest.until}"))
    lines.append("")
    lines.append(
        f"**{digest.total_commits} commit(s)** across "
        f"**{digest.total_authors} contributor(s)**"
    )
    lines.append("")

    for summary in digest.authors:
        lines.append(_md_header(2, summary.author))
        lines.append(f"- Commits: {summary.commit_count}")
        lines.append(f"- Files touched: {summary.files_touched}")
        lines.append("")
        lines.append("**Changes:**")
        for subject in summary.subjects:
            lines.append(f"  - {subject}")
        lines.append("")

    return "\n".join(lines)


def render_plain(digest: WeeklyDigest) -> str:
    lines: list[str] = []
    lines.append(f"Weekly Digest: {digest.since} – {digest.until}")
    lines.append("=" * 40)
    lines.append(
        f"{digest.total_commits} commit(s), {digest.total_authors} contributor(s)"
    )
    lines.append("")

    for summary in digest.authors:
        lines.append(f"[{summary.author}]")
        lines.append(f"  Commits      : {summary.commit_count}")
        lines.append(f"  Files touched: {summary.files_touched}")
        lines.append("  Changes:")
        for subject in summary.subjects:
            lines.append(f"    * {subject}")
        lines.append("")

    return "\n".join(lines)


def render(digest: WeeklyDigest, fmt: OutputFormat = "markdown") -> str:
    """Render a WeeklyDigest to the requested format string."""
    if fmt == "markdown":
        return render_markdown(digest)
    if fmt == "plain":
        return render_plain(digest)
    raise ValueError(f"Unknown output format: {fmt!r}")
