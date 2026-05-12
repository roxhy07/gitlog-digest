"""Tests for gitlog_digest.output_writer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gitlog_digest.output_writer import (
    choose_extension,
    default_output_path,
    write_output,
)


CONTENT = "# Hello\nsome digest text\n"


class TestWriteOutputStdout:
    def test_writes_to_stdout(self, capsys):
        write_output(CONTENT, path=None)
        captured = capsys.readouterr()
        assert "# Hello" in captured.out

    def test_appends_newline_if_missing(self, capsys):
        write_output("no newline", path=None)
        captured = capsys.readouterr()
        assert captured.out.endswith("\n")

    def test_does_not_double_newline(self, capsys):
        write_output("already\n", path=None)
        captured = capsys.readouterr()
        assert captured.out == "already\n"


class TestWriteOutputFile:
    def test_creates_file(self, tmp_path):
        dest = tmp_path / "out.md"
        write_output(CONTENT, path=str(dest))
        assert dest.exists()

    def test_file_content_matches(self, tmp_path):
        dest = tmp_path / "out.md"
        write_output(CONTENT, path=str(dest))
        assert dest.read_text(encoding="utf-8") == CONTENT

    def test_creates_parent_dirs(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.txt"
        write_output("hello", path=str(dest))
        assert dest.exists()

    def test_stderr_message(self, tmp_path, capsys):
        dest = tmp_path / "out.md"
        write_output(CONTENT, path=str(dest))
        captured = capsys.readouterr()
        assert str(dest) in captured.err


class TestChooseExtension:
    def test_markdown_gives_md(self):
        assert choose_extension("markdown") == ".md"

    def test_plain_gives_txt(self):
        assert choose_extension("plain") == ".txt"

    def test_unknown_gives_txt(self):
        assert choose_extension("whatever") == ".txt"


class TestDefaultOutputPath:
    def test_markdown_filename(self):
        path = default_output_path("2024-01-08", "2024-01-14", "markdown")
        assert path == "digest_2024-01-08_2024-01-14.md"

    def test_plain_filename(self):
        path = default_output_path("2024-01-08", "2024-01-14", "plain")
        assert path == "digest_2024-01-08_2024-01-14.txt"
