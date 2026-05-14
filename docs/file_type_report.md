# File-Type Report

The file-type report gives a quick overview of which languages and file
categories saw the most activity during the digest period.

## What it tracks

| Field | Description |
|-------|-------------|
| `extension` | Normalised file extension (e.g. `.py`, `.md`) or `<no ext>` |
| `file_count` | Number of **unique** file paths with that extension |
| `commit_count` | Number of distinct commits that touched at least one file of this type |
| `authors` | Sorted list of contributors who changed files of this type |

## Usage

```python
from gitlog_digest.file_type_report import (
    build_file_type_map,
    top_n_types,
    format_file_type_section,
)

commits = fetch_commits(repo=".", since="2024-01-01")
mapping = build_file_type_map(commits)
top = top_n_types(mapping, n=10)
print(format_file_type_section(top))
```

### Example output

```
File-type breakdown:

  .py          [####################]   42 file(s)  18 commit(s)
  .md          [########------------]   17 file(s)   9 commit(s)
  .yml         [####----------------]    8 file(s)   5 commit(s)
  <no ext>     [##------------------]    4 file(s)   3 commit(s)
```

## Notes

- File paths are deduplicated per extension, so renaming a file and editing
  it in the same week counts as **one** unique file.
- The bar width can be adjusted via the `bar_width` parameter of
  `format_file_type_section` (default `20`).
- Extensions are lower-cased so `.PY` and `.py` are treated identically.
