"""Configuration loading for gitlog-digest.

Supports reading defaults from a .gitlog-digest.toml file
in the repo root or user home directory.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_NAMES = [".gitlog-digest.toml", "gitlog-digest.toml"]


@dataclass
class DigestConfig:
    output_format: str = "markdown"
    output_dir: str = "."
    since_days: int = 7
    exclude_authors: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    max_subject_length: int = 72


def _find_config_file(start: Path) -> Path | None:
    """Walk up from start looking for a config file, then check home dir."""
    current = start.resolve()
    for directory in [current, *current.parents]:
        for name in DEFAULT_CONFIG_NAMES:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    for name in DEFAULT_CONFIG_NAMES:
        candidate = Path.home() / name
        if candidate.is_file():
            return candidate
    return None


def load_config(repo_path: str | Path = ".") -> DigestConfig:
    """Load config from file if present, otherwise return defaults."""
    config_file = _find_config_file(Path(repo_path))
    if config_file is None:
        return DigestConfig()

    with config_file.open("rb") as fh:
        raw = tomllib.load(fh)

    section = raw.get("gitlog-digest", raw)
    return DigestConfig(
        output_format=section.get("output_format", "markdown"),
        output_dir=section.get("output_dir", "."),
        since_days=int(section.get("since_days", 7)),
        exclude_authors=list(section.get("exclude_authors", [])),
        exclude_patterns=list(section.get("exclude_patterns", [])),
        max_subject_length=int(section.get("max_subject_length", 72)),
    )
