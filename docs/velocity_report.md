# Velocity Report

The velocity report shows how commit activity is distributed over time,
highlighting peak days and weeks.

## What it measures

- **Daily counts** — number of commits on each calendar day.
- **Weekly counts** — commits grouped into ISO weeks (Monday-start).
- **Average daily velocity** — mean commits per active day.
- **Peak day / peak week** — the single busiest day and week in the range.

## CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--velocity` | off | Append a velocity section to the digest output. |
| `--velocity-top-n N` | `7` | How many top days to list in the bar chart. |

### Example

```bash
gitlog-digest --since 2024-01-01 --until 2024-01-31 --velocity --velocity-top-n 5
```

Sample output:

```
## Commit Velocity
  Average commits/day : 2.4
  Peak day            : 2024-01-15 (8 commits)
  Peak week           : 2024-01-15 (21 commits)

  Top days:
    2024-01-08  ████████░░░░░░░░░░░░  5
    2024-01-10  ██████░░░░░░░░░░░░░░  4
    2024-01-15  ████████████████████  8
    2024-01-22  ████░░░░░░░░░░░░░░░░  3
    2024-01-29  ██░░░░░░░░░░░░░░░░░░  2
```

## Programmatic API

```python
from gitlog_digest.velocity_report import build_velocity_report, format_velocity_section

report = build_velocity_report(commits)
print(report.average_daily())
print(report.peak_day())
print(format_velocity_section(report, top_n=10))
```

## Integration with the summary header

A one-liner suitable for digest headers is available via `velocity_cli`:

```python
from gitlog_digest.velocity_cli import velocity_summary_line

print(velocity_summary_line(commits))
# Velocity: 2.4 commits/day avg, peak 2024-01-15 (8)
```
