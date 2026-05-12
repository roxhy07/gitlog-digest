# Blame Integration

`gitlog_digest.blame` provides lightweight helpers that run `git blame` on
individual files and summarise ownership by author line count.

## Overview

The module exposes three public functions:

| Function | Description |
|---|---|
| `blame_file(repo, filepath)` | Blame a single file, returns `FileBlame` |
| `blame_files(repo, filepaths)` | Blame multiple files, skips failures |
| `parse_blame_output(lines)` | Parse raw porcelain lines into `{author: count}` |

## FileBlame dataclass

```python
@dataclass
class FileBlame:
    path: str
    line_counts: Dict[str, int]   # author name -> line count

    top_author: Optional[str]     # property — highest line count
    total_lines: int              # property — sum of all counts
```

## Basic usage

```python
from gitlog_digest.blame import blame_files

files = ["gitlog_digest/cli.py", "gitlog_digest/renderer.py"]
results = blame_files("/path/to/repo", files)

for fb in results:
    print(f"{fb.path}: top contributor is {fb.top_author} ({fb.total_lines} lines)")
```

## Integration with diff_stats

You can combine `blame_files` with the file list produced by
`aggregate_diff_stats` to highlight ownership of recently changed files:

```python
from gitlog_digest.diff_stats import aggregate_diff_stats
from gitlog_digest.blame import blame_files

stats = aggregate_diff_stats(commits)
changed = list(stats.by_file.keys())
blame_results = blame_files(repo, changed)
```

## Notes

- Files with no blame output (e.g. binary files, deleted files) are silently
  skipped by `blame_files`.
- The module calls `git blame --porcelain`; ensure `git` is on `PATH`.
- Blame can be slow on large files — consider caching results with
  `gitlog_digest.cache`.
