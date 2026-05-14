"""Commit trend analysis: buckets commits by weekday or hour for activity heatmaps."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOUR_BLOCK_SIZE = 4  # group hours into 4-hour buckets


@dataclass
class TrendReport:
    by_weekday: Dict[str, int] = field(default_factory=dict)
    by_hour_block: Dict[str, int] = field(default_factory=dict)

    def busiest_day(self) -> str | None:
        if not self.by_weekday:
            return None
        return max(self.by_weekday, key=lambda k: self.by_weekday[k])

    def busiest_hour_block(self) -> str | None:
        if not self.by_hour_block:
            return None
        return max(self.by_hour_block, key=lambda k: self.by_hour_block[k])


def _hour_block_label(hour: int) -> str:
    start = (hour // HOUR_BLOCK_SIZE) * HOUR_BLOCK_SIZE
    end = start + HOUR_BLOCK_SIZE
    return f"{start:02d}:00-{end:02d}:00"


def build_trend_report(commits: List) -> TrendReport:
    """Analyse commit timestamps and return bucketed activity counts."""
    weekday_counter: Counter = Counter()
    hour_counter: Counter = Counter()

    for commit in commits:
        dt = getattr(commit, "date", None)
        if dt is None:
            continue
        weekday_counter[DAY_NAMES[dt.weekday()]] += 1
        hour_counter[_hour_block_label(dt.hour)] += 1

    by_weekday = {day: weekday_counter.get(day, 0) for day in DAY_NAMES}
    all_blocks = sorted({_hour_block_label(h) for h in range(0, 24)})
    by_hour_block = {blk: hour_counter.get(blk, 0) for blk in all_blocks}

    return TrendReport(by_weekday=by_weekday, by_hour_block=by_hour_block)


def format_trend_report(report: TrendReport, bar_width: int = 20) -> str:
    """Render a plain-text trend report with mini bar charts."""
    if not any(report.by_weekday.values()):
        return ""

    lines = ["## Activity Trends", "", "**By weekday:**"]
    max_day = max(report.by_weekday.values(), default=1) or 1
    for day, count in report.by_weekday.items():
        bar_len = round(count / max_day * bar_width)
        bar = "█" * bar_len
        lines.append(f"  {day}  {bar:<{bar_width}}  {count}")

    lines += ["", "**By time of day:**"]
    max_hour = max(report.by_hour_block.values(), default=1) or 1
    for block, count in report.by_hour_block.items():
        bar_len = round(count / max_hour * bar_width)
        bar = "█" * bar_len
        lines.append(f"  {block}  {bar:<{bar_width}}  {count}")

    busiest = report.busiest_day()
    if busiest:
        lines += ["", f"Most active day: **{busiest}**"]

    return "\n".join(lines)
