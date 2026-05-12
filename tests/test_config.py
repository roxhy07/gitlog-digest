"""Tests for gitlog_digest.config."""

import textwrap
from pathlib import Path

import pytest

from gitlog_digest.config import DigestConfig, load_config, _find_config_file


class TestDigestConfigDefaults:
    def test_default_format_is_markdown(self):
        cfg = DigestConfig()
        assert cfg.output_format == "markdown"

    def test_default_since_days(self):
        cfg = DigestConfig()
        assert cfg.since_days == 7

    def test_default_exclude_authors_empty(self):
        cfg = DigestConfig()
        assert cfg.exclude_authors == []

    def test_default_max_subject_length(self):
        cfg = DigestConfig()
        assert cfg.max_subject_length == 72


class TestLoadConfig:
    def test_returns_defaults_when_no_file(self, tmp_path):
        cfg = load_config(tmp_path)
        assert isinstance(cfg, DigestConfig)
        assert cfg.output_format == "markdown"

    def test_reads_output_format(self, tmp_path):
        toml = textwrap.dedent("""\
            [gitlog-digest]
            output_format = "plain"
        """)
        (tmp_path / ".gitlog-digest.toml").write_text(toml)
        cfg = load_config(tmp_path)
        assert cfg.output_format == "plain"

    def test_reads_since_days(self, tmp_path):
        toml = textwrap.dedent("""\
            [gitlog-digest]
            since_days = 14
        """)
        (tmp_path / ".gitlog-digest.toml").write_text(toml)
        cfg = load_config(tmp_path)
        assert cfg.since_days == 14

    def test_reads_exclude_authors(self, tmp_path):
        toml = textwrap.dedent("""\
            [gitlog-digest]
            exclude_authors = ["bot", "ci"]
        """)
        (tmp_path / ".gitlog-digest.toml").write_text(toml)
        cfg = load_config(tmp_path)
        assert cfg.exclude_authors == ["bot", "ci"]

    def test_reads_exclude_patterns(self, tmp_path):
        toml = textwrap.dedent("""\
            [gitlog-digest]
            exclude_patterns = ["chore:*", "Merge *"]
        """)
        (tmp_path / ".gitlog-digest.toml").write_text(toml)
        cfg = load_config(tmp_path)
        assert cfg.exclude_patterns == ["chore:*", "Merge *"]

    def test_finds_config_in_parent(self, tmp_path):
        toml = "[gitlog-digest]\noutput_format = \"plain\"\n"
        (tmp_path / ".gitlog-digest.toml").write_text(toml)
        subdir = tmp_path / "src" / "pkg"
        subdir.mkdir(parents=True)
        cfg = load_config(subdir)
        assert cfg.output_format == "plain"

    def test_top_level_keys_without_section(self, tmp_path):
        toml = "output_format = \"plain\"\nsince_days = 3\n"
        (tmp_path / "gitlog-digest.toml").write_text(toml)
        cfg = load_config(tmp_path)
        assert cfg.output_format == "plain"
        assert cfg.since_days == 3


class TestFindConfigFile:
    def test_returns_none_when_absent(self, tmp_path):
        result = _find_config_file(tmp_path)
        assert result is None

    def test_finds_dotfile_in_same_dir(self, tmp_path):
        f = tmp_path / ".gitlog-digest.toml"
        f.write_text("")
        assert _find_config_file(tmp_path) == f
