# Review Report

The `review_report` module aggregates commit history into a per-author
code-review activity summary, useful for async standups and sprint retrospectives.

## Overview

For each author in the selected date range the report shows:

- Number of commits
- Number of **unique** files touched (duplicates across commits are collapsed)
- A proportional ASCII activity bar relative to the most-active author

## Data Structures

### `ReviewEntry`

| Field | Type | Description |
|---|---|---|
| `author` | `str` | Commit author name |
| `commit_count` | `int` | Total commits in range |
| `files_touched` | `int` | Unique files modified |
| `subjects` | `list[str]` | Commit subject lines |

## Functions

### `build_review_entries(commits)`

Accepts a list of `Commit` objects and returns a list of `ReviewEntry` values
sorted by `commit_count` descending.

```python
from gitlog_digest.git_parser import fetch_commits
from gitlog_digest.review_report import build_review_entries

commits = fetch_commits(repo=".", since="2024-01-01", until="2024-01-07")
entries = build_review_entries(commits)
for e in entries:
    print(e.author, e.commit_count, e.files_touched)
```

### `format_review_section(entries)`

Renders the entries as a Markdown-compatible plain-text section.
Returns an empty string when `entries` is empty.

## Example Output

```
## Code Review Activity

  Alice                [####################] 8 commit(s), 14 file(s)
  Bob                  [##########----------] 4 commit(s), 6 file(s)
  Carol                [#####---------------] 2 commit(s), 3 file(s)
```

## Integration

The section is intended to be appended to the output produced by
`gitlog_digest.renderer.render` when the `--review` CLI flag is supplied.
