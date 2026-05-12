# gitlog-digest

Generates readable weekly summaries from git history for async team standups.

---

## Installation

```bash
pip install gitlog-digest
```

Or install from source:

```bash
git clone https://github.com/yourname/gitlog-digest && pip install -e .
```

---

## Usage

Run inside any git repository to generate a summary for the past week:

```bash
gitlog-digest
```

Specify a custom date range or output format:

```bash
# Summarize the last 14 days
gitlog-digest --days 14

# Output as Markdown file
gitlog-digest --format markdown --output digest.md

# Filter by author
gitlog-digest --author "Jane Doe"
```

Example output:

```
Weekly Digest — May 12 to May 19, 2025
───────────────────────────────────────
👤 Jane Doe (8 commits)
  • Refactored authentication middleware
  • Added unit tests for user service
  • Fixed pagination bug in dashboard API

👤 John Smith (5 commits)
  • Updated dependencies
  • Improved CI pipeline configuration
```

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--days` | `7` | Number of days to look back |
| `--author` | all | Filter commits by author name |
| `--format` | `text` | Output format: `text` or `markdown` |
| `--output` | stdout | Write output to a file |

---

## License

MIT © 2025 yourname