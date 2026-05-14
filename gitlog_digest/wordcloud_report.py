"""Build a simple word-frequency map from commit subjects."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

# Common words to ignore when building the frequency map.
_STOPWORDS = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "be", "been", "as",
        "it", "its", "this", "that", "into", "up", "not", "no", "so",
    }
)


@dataclass
class WordFrequency:
    word: str
    count: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"WordFrequency({self.word!r}, count={self.count})"


def _tokenise(text: str) -> List[str]:
    """Lower-case and split *text* into alphabetic tokens."""
    return re.findall(r"[a-z]+", text.lower())


def build_word_frequencies(
    commits: Iterable,
    stopwords: frozenset = _STOPWORDS,
    min_length: int = 3,
) -> List[WordFrequency]:
    """Return word frequencies sorted descending by count."""
    counter: Counter = Counter()
    for commit in commits:
        subject = getattr(commit, "subject", "") or ""
        for token in _tokenise(subject):
            if len(token) >= min_length and token not in stopwords:
                counter[token] += 1
    return [
        WordFrequency(word=w, count=c)
        for w, c in counter.most_common()
    ]


def top_n_words(frequencies: List[WordFrequency], n: int = 10) -> List[WordFrequency]:
    """Return at most *n* entries (already sorted)."""
    return frequencies[:n]


def format_wordcloud_section(frequencies: List[WordFrequency], n: int = 10) -> str:
    """Render a plain-text word-frequency table."""
    top = top_n_words(frequencies, n)
    if not top:
        return ""
    max_count = top[0].count
    lines = ["## Top Words in Commit Messages", ""]
    for wf in top:
        bar_len = int(20 * wf.count / max_count) if max_count else 0
        bar = "█" * bar_len
        lines.append(f"  {wf.word:<20} {bar:<20} {wf.count}")
    lines.append("")
    return "\n".join(lines)
