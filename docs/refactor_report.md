# Refactor Report

The **refactor report** surfaces commits that look like code quality improvements — refactors, cleanups, renames, and similar housekeeping work — so teams can celebrate and track this often-invisible effort.

## How it works

Each commit subject is scanned for a set of well-known refactor-related keywords:

- `refactor`, `restructure`, `reorganise` / `reorganize`
- `cleanup`, `clean up`, `tidy`
- `rename`, `move`, `extract`
- `simplify`, `dedup`, `deduplicate`

Matching is **case-insensitive** and checks for substring presence, so `"Refactor: split auth module"` and `"cleanup legacy helpers"` are both detected.

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `--refactor` | off | Include the refactor section in the digest |
| `--top-refactorers N` | `5` | Show the top N authors by refactor commit count |

### Example

```
gitlog-digest --refactor --top-refactorers 3
```

## Output example

```
Refactor Activity
-----------------
  alice: 4 refactor commit(s)
    - refactor: extract auth helpers
    - cleanup old session code
    - rename config keys for clarity
    … and 1 more
  bob: 1 refactor commit(s)
    - simplify retry logic
```

## Programmatic use

```python
from gitlog_digest.refactor_report import build_refactor_map, top_refactorers, format_refactor_section

refactor_map = build_refactor_map(commits)
entries = top_refactorers(refactor_map, n=5)
print(format_refactor_section(entries))
```

## Data model

`RefactorEntry` holds:
- `author` — commit author name
- `subjects` — list of matching commit subjects
- `count` — number of refactor commits (derived property)
