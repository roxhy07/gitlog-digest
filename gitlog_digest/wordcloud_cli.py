"""CLI helpers for the wordcloud report feature."""

from __future__ import annotations

import argparse
from typing import List

from gitlog_digest.wordcloud_report import (
    build_word_frequencies,
    format_wordcloud_section,
)


def add_wordcloud_flag(parser: argparse.ArgumentParser) -> None:
    """Register --wordcloud and --wordcloud-top-n flags on *parser*."""
    parser.add_argument(
        "--wordcloud",
        action="store_true",
        default=False,
        help="Append a word-frequency summary of commit messages.",
    )
    parser.add_argument(
        "--wordcloud-top-n",
        type=int,
        default=10,
        metavar="N",
        dest="wordcloud_top_n",
        help="Number of top words to display (default: 10).",
    )


def maybe_render_wordcloud(args: argparse.Namespace, commits: List) -> str:
    """Return the formatted wordcloud section if the flag is set, else ''."""
    if not getattr(args, "wordcloud", False):
        return ""
    n = getattr(args, "wordcloud_top_n", 10)
    frequencies = build_word_frequencies(commits)
    return format_wordcloud_section(frequencies, n=n)


def wordcloud_summary_line(commits: List, n: int = 5) -> str:
    """Return a one-line summary of the top *n* words, e.g. for footers."""
    frequencies = build_word_frequencies(commits)
    top = frequencies[:n]
    if not top:
        return ""
    words = ", ".join(wf.word for wf in top)
    return f"Top words: {words}"
