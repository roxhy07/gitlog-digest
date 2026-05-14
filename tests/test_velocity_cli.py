"""Tests for gitlog_digest.velocity_cli."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from gitlog_digest.velocity_cli import (
    add_velocity_flag,
    maybe_render_velocity,
    velocity_summary_line,
)


def make_commit(day: date):
    c = MagicMock()
    c.date = datetime(day.year, day.month, day.day, 9, 0, 0)
    c.subject = "chore: something"
    return c


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_velocity_flag(p)
    return p


MON = date(2024, 3, 4)
TUE = date(2024, 3, 5)


class TestAddVelocityFlag:
    def test_flag_default_false(self):
        args = _make_parser().parse_args([])
        assert args.velocity is False

    def test_flag_enabled(self):
        args = _make_parser().parse_args(["--velocity"])
        assert args.velocity is True

    def test_top_n_default(self):
        args = _make_parser().parse_args([])
        assert args.velocity_top_n == 7

    def test_top_n_custom(self):
        args = _make_parser().parse_args(["--velocity-top-n", "3"])
        assert args.velocity_top_n == 3


class TestMaybeRenderVelocity:
    def _args(self, velocity: bool = False, top_n: int = 7) -> argparse.Namespace:
        return argparse.Namespace(velocity=velocity, velocity_top_n=top_n)

    def test_returns_empty_when_flag_off(self):
        commits = [make_commit(MON)]
        result = maybe_render_velocity(self._args(velocity=False), commits)
        assert result == ""

    def test_returns_section_when_flag_on(self):
        commits = [make_commit(MON), make_commit(TUE)]
        result = maybe_render_velocity(self._args(velocity=True), commits)
        assert "Commit Velocity" in result

    def test_respects_top_n(self):
        days = [date(2024, 3, i) for i in range(1, 12)]
        commits = [make_commit(d) for d in days]
        result = maybe_render_velocity(self._args(velocity=True, top_n=2), commits)
        rows = [l for l in result.splitlines() if l.startswith("    2024")]
        assert len(rows) == 2

    def test_missing_velocity_attr_returns_empty(self):
        args = argparse.Namespace()  # no velocity attr
        assert maybe_render_velocity(args, [make_commit(MON)]) == ""


class TestVelocitySummaryLine:
    def test_no_commits_returns_no_data(self):
        assert velocity_summary_line([]) == "Velocity: no data"

    def test_contains_avg_and_peak(self):
        commits = [make_commit(MON), make_commit(MON), make_commit(TUE)]
        line = velocity_summary_line(commits)
        assert "commits/day avg" in line
        assert str(MON) in line

    def test_single_commit(self):
        line = velocity_summary_line([make_commit(MON)])
        assert "1.0 commits/day avg" in line
