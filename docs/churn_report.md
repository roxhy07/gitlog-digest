# File Churn Report

The **churn report** identifies which files are changed most frequently across
the commits in a digest window. High-churn files often indicate hotspots that
may benefit from refactoring or closer review.

## How it works

1. Every commit's `files_changed` list is iterated.
2. A counter tracks how many commits touched each filepath.
3. The top-N files (default **10**) are returned as `ChurnEntry` objects.
4. An ASCII bar chart is rendered proportional to the highest churn count.

## API

### `build_churn_map(commits) -> Counter`

Returns a raw `collections.Counter` mapping each filepath to the number of
commits that modified it. Useful when you need the raw data for further
processing.

### `top_churned_files(commits, n=10) -> List[ChurnEntry]`

Convenience wrapper around `build_churn_map` that returns a sorted list of
`ChurnEntry` objects (highest churn first), truncated to *n* entries.

### `format_churn_section(entries, width=20) -> str`

Renders a Markdown-compatible plain-text section ready for inclusion in a
weekly digest. Each row shows an ASCII bar, the change count, and the
filepath.

## Example output

```
## File Churn

  ████████████████████   12x  src/core/engine.py
  ██████████░░░░░░░░░░    6x  gitlog_digest/cli.py
  █████░░░░░░░░░░░░░░░    3x  tests/test_cli.py
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `churn_top_n` | `10` | Maximum number of files to include in the report |
| `churn_bar_width` | `20` | Character width of the ASCII bar |

These options can be set in `.gitlog-digest.toml` under the `[churn]` table.
