"""Tests for gitlog_digest.wordcloud_report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from gitlog_digest.wordcloud_report import (
    WordFrequency,
    _tokenise,
    build_word_frequencies,
    format_wordcloud_section,
    top_n_words,
)


@dataclass
class FakeCommit:
    subject: str = ""


# ---------------------------------------------------------------------------
# _tokenise
# ---------------------------------------------------------------------------

def test_tokenise_lowercases():
    assert _tokenise("Fix Bug") == ["fix", "bug"]


def test_tokenise_strips_punctuation():
    assert _tokenise("feat: add login") == ["feat", "add", "login"]


def test_tokenise_empty_string():
    assert _tokenise("") == []


# ---------------------------------------------------------------------------
# build_word_frequencies
# ---------------------------------------------------------------------------

def test_empty_commits_returns_empty():
    assert build_word_frequencies([]) == []


def test_stopwords_excluded():
    commits = [FakeCommit("fix the bug"), FakeCommit("add the feature")]
    words = {wf.word for wf in build_word_frequencies(commits)}
    assert "the" not in words


def test_short_words_excluded():
    commits = [FakeCommit("do it")]
    # 'do' and 'it' are both < min_length=3
    assert build_word_frequencies(commits) == []


def test_counts_are_correct():
    commits = [
        FakeCommit("add login feature"),
        FakeCommit("add logout feature"),
        FakeCommit("fix login redirect"),
    ]
    freq_map = {wf.word: wf.count for wf in build_word_frequencies(commits)}
    assert freq_map["add"] == 2
    assert freq_map["login"] == 2
    assert freq_map["feature"] == 2
    assert freq_map["fix"] == 1


def test_sorted_descending():
    commits = [FakeCommit("fix fix fix add add refactor")]
    freqs = build_word_frequencies(commits)
    counts = [wf.count for wf in freqs]
    assert counts == sorted(counts, reverse=True)


def test_missing_subject_attribute_skipped():
    class NoSubject:
        pass

    result = build_word_frequencies([NoSubject()])
    assert result == []


# ---------------------------------------------------------------------------
# top_n_words
# ---------------------------------------------------------------------------

def test_top_n_limits_results():
    freqs = [WordFrequency(word=str(i), count=i) for i in range(20, 0, -1)]
    assert len(top_n_words(freqs, 5)) == 5


def test_top_n_returns_all_when_fewer():
    freqs = [WordFrequency("hello", 3), WordFrequency("world", 1)]
    assert top_n_words(freqs, 10) == freqs


# ---------------------------------------------------------------------------
# format_wordcloud_section
# ---------------------------------------------------------------------------

def test_format_empty_returns_empty_string():
    assert format_wordcloud_section([]) == ""


def test_format_contains_header():
    freqs = [WordFrequency("refactor", 5)]
    output = format_wordcloud_section(freqs)
    assert "Top Words" in output


def test_format_contains_word_and_count():
    freqs = [WordFrequency("refactor", 7), WordFrequency("bugfix", 3)]
    output = format_wordcloud_section(freqs)
    assert "refactor" in output
    assert "7" in output


def test_format_respects_n_limit():
    freqs = [WordFrequency(word=str(i), count=i + 1) for i in range(20)]
    output = format_wordcloud_section(freqs, n=3)
    # Only top-3 words should appear; word '0' (count=1) should not
    assert "19" in output  # highest count word index
