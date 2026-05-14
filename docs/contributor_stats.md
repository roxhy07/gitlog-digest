# Contributor Statistics

`gitlog_digest` can aggregate per-contributor activity metrics across any date
range and render them as a ranked leaderboard inside your digest.

## What Is Tracked

| Metric | Description |
|---|---|
| `commit_count` | Total commits authored in the period |
| `lines_added` | Sum of inserted lines across all commits |
| `lines_deleted` | Sum of deleted lines across all commits |
| `net_lines` | `lines_added - lines_deleted` |
| `unique_files` | Distinct file paths touched (deduplicated) |

## Python API

```python
from gitlog_digest.git_parser import fetch_commits
from gitlog_digest.contributor_stats import build_contributor_stats, rank_contributors
from gitlog_digest.contributor_report import format_contributor_section

commits = fetch_commits(repo=".", since="2024-01-01", until="2024-01-07")
stats = build_contributor_stats(commits)

# rank by commit count (default)
ranked = rank_contributors(stats)

# or rank by lines added
ranked = rank_contributors(stats, by="lines_added")

# render as text
print(format_contributor_section(stats, top_n=5))
```

## Output Example

```
## Top Contributors

  Alice                ████████████████████   42 commits  +1240/-380  17 files
  Carol                ████████████░░░░░░░░   26 commits  +870/-210   12 files
  Bob                  ██████░░░░░░░░░░░░░░   13 commits  +340/-90     8 files
```

## Sorting Options

Pass `sort_by` to `format_contributor_section` (or `rank_contributors`) to
change the ordering:

- `"commit_count"` *(default)*
- `"lines_added"`
- `"net_lines"`
- `"unique_files"`

## Notes

- Line counts are sourced from `git log --numstat`; binary files are skipped.
- Authors are matched exactly as returned by git (respects `.mailmap`).
