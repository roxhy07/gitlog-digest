"""Tests for gitlog_digest.cache_cli."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from gitlog_digest.cache import save_cache
from gitlog_digest.cache_cli import add_cache_subparser, handle_cache_command

SAMPLE = [{"hash": "abc", "author": "Alice", "subject": "init"}]


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_cache_subparser(sub)
    return parser


def test_clear_removes_files(tmp_path, capsys):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE, cache_dir=tmp_path)
    parser = _make_parser()
    args = parser.parse_args(["cache", "clear", "--dir", str(tmp_path)])
    args.func(args)
    captured = capsys.readouterr()
    assert "Removed 1" in captured.out
    assert list(tmp_path.glob("*.json")) == []


def test_clear_empty_dir(tmp_path, capsys):
    parser = _make_parser()
    args = parser.parse_args(["cache", "clear", "--dir", str(tmp_path)])
    args.func(args)
    captured = capsys.readouterr()
    assert "Removed 0" in captured.out


def test_status_shows_count(tmp_path, capsys):
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE, cache_dir=tmp_path)
    save_cache("/repo", "2024-01-08", "2024-01-14", SAMPLE, cache_dir=tmp_path)
    parser = _make_parser()
    args = parser.parse_args(["cache", "status", "--dir", str(tmp_path)])
    args.func(args)
    captured = capsys.readouterr()
    assert "2" in captured.out


def test_status_missing_dir(tmp_path, capsys):
    missing = tmp_path / "nope"
    parser = _make_parser()
    args = parser.parse_args(["cache", "status", "--dir", str(missing)])
    args.func(args)
    captured = capsys.readouterr()
    assert "does not exist" in captured.out


def test_status_shows_directory_path(tmp_path, capsys):
    parser = _make_parser()
    save_cache("/repo", "2024-01-01", "2024-01-07", SAMPLE, cache_dir=tmp_path)
    args = parser.parse_args(["cache", "status", "--dir", str(tmp_path)])
    args.func(args)
    captured = capsys.readouterr()
    assert str(tmp_path) in captured.out


def test_subparser_registered():
    parser = _make_parser()
    # Should not raise
    args = parser.parse_args(["cache", "clear"])
    assert args.command == "cache"
    assert args.cache_cmd == "clear"
