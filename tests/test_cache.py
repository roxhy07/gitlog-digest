"""Tests for gitlog_digest.cache."""

import json
import time
from pathlib import Path

import pytest

from gitlog_digest.cache import (
    _cache_key,
    clear_cache,
    load_cache,
    save_cache,
)

SAMPLE_COMMITS = [
    {"hash": "abc1234", "author": "Alice", "subject": "fix bug"},
    {"hash": "def5678", "author": "Bob", "subject": "add feature"},
]


def test_cache_key_is_stable():
    k1 = _cache_key("/repo", "2024-01-01", "2024-01-07")
    k2 = _cache_key("/repo", "2024-01-01", "2024-01-07")
    assert k1 == k2


def test_cache_key_differs_on_params():
    k1 = _cache_key("/repo", "2024-01-01", "2024-01-07")
    k2 = _cache_key("/repo", "2024-01-08", "2024-01-14")
    assert k1 != k2


def test_cache_key_length():
    key = _cache_key("/repo", "2024-01-01", "2024-01-07")
    assert len(key) == 16


def test_save_and_load_roundtrip(tmp_path):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE_COMMITS, cache_dir=tmp_path)
    result = load_cache("/repo", "2024-01-01", "2024-01-07", cache_dir=tmp_path, ttl=60)
    assert result == SAMPLE_COMMITS


def test_load_returns_none_when_missing(tmp_path):
    result = load_cache("/repo", "2024-01-01", "2024-01-07", cache_dir=tmp_path)
    assert result is None


def test_load_returns_none_when_expired(tmp_path):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE_COMMITS, cache_dir=tmp_path)
    # Force expiry by setting ttl=0
    result = load_cache("/repo", "2024-01-01", "2024-01-07", cache_dir=tmp_path, ttl=0)
    assert result is None


def test_load_returns_none_on_corrupt_file(tmp_path):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE_COMMITS, cache_dir=tmp_path)
    # Corrupt the file
    for p in tmp_path.glob("*.json"):
        p.write_text("not json{{{")
    result = load_cache("/repo", "2024-01-01", "2024-01-07", cache_dir=tmp_path)
    assert result is None


def test_clear_cache_removes_files(tmp_path):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE_COMMITS, cache_dir=tmp_path)
    save_cache("/repo", "2024-01-08", "2024-01-14", SAMPLE_COMMITS, cache_dir=tmp_path)
    removed = clear_cache(cache_dir=tmp_path)
    assert removed == 2
    assert list(tmp_path.glob("*.json")) == []


def test_clear_cache_on_missing_dir(tmp_path):
    missing = tmp_path / "nonexistent"
    removed = clear_cache(cache_dir=missing)
    assert removed == 0


def test_save_creates_cache_dir(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE_COMMITS, cache_dir=nested)
    assert nested.exists()
    assert len(list(nested.glob("*.json"))) == 1
