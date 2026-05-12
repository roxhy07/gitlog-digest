# Diff Statistics

`gitlog_digest` can surface lightweight diff statistics alongside the commit
summaries, giving readers a quick sense of how much code changed in a period.

## What is tracked

| Metric | Description |
|---|---|
| `total_insertions` | Sum of lines added across all commits |
| `total_deletions` | Sum of lines removed across all commits |
| `net_lines` | `insertions − deletions` |
| `unique_file_count` | Number of distinct files touched |

## How it works

Each `Commit` object carries optional `insertions`, `deletions`, and
`files_changed` fields that are populated by `fetch_commits` when git's
`--numstat` output is requested.

`aggregate_diff_stats(commits)` iterates over the list and accumulates totals
into a `DiffStats` dataclass.

```python
from gitlog_digest.diff_stats import aggregate_diff_stats, format_diff_stats
from gitlog_digest.git_parser import fetch_commits

commits = fetch_commits(repo=".", since="2024-01-01")
stats = aggregate_diff_stats(commits)
print(format_diff_stats(stats))
# 14 files changed, +312 insertions, -87 deletions (net +225)
```

## Parsing raw numstat lines

If you feed raw `git diff --numstat` output into the library you can parse
individual lines with `parse_numstat_line`:

```python
from gitlog_digest.diff_stats import parse_numstat_line

result = parse_numstat_line("42\t7\tsrc/app.py")
# (42, 7, 'src/app.py')
```

Binary files (where git outputs `-` instead of a number) return `None` and
are silently skipped during aggregation.

## Notes

- Diff stats are **optional**. If `insertions`/`deletions` are absent from a
  `Commit` they default to `0` and do not affect totals.
- The `changed_files` list may contain duplicates across commits; deduplication
  happens inside `DiffStats.unique_file_count` via a `set` conversion.
