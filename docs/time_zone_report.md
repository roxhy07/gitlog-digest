# Time Zone Report

The **time zone report** surfaces the UTC offsets embedded in each commit's
timestamp, making it easy to see where your contributors are working from and
spot when people are committing outside their normal hours.

## How it works

Git stores a UTC offset alongside every commit timestamp in ISO-8601 format
(e.g. `2024-03-15T09:42:00+02:00`).  `time_zone_report` parses that suffix
and groups offsets by author.

## Key types

### `TimeZoneEntry`

| Attribute | Type | Description |
|---|---|---|
| `author` | `str` | Commit author name |
| `offsets` | `list[str]` | All observed offsets in commit order |
| `primary_offset` | `str \| None` | Most frequently seen offset |
| `unique_offsets` | `list[str]` | Deduplicated offsets, insertion order |

## Public API

```python
from gitlog_digest.time_zone_report import build_time_zone_map, format_time_zone_section

# commits: any sequence with .author and .date attributes
entries = build_time_zone_map(commits)
print(format_time_zone_section(entries, top_n=10))
```

### `build_time_zone_map(commits)`

Returns `dict[str, TimeZoneEntry]` keyed by author name.  Commits whose
`date` field cannot be parsed are silently skipped (offset omitted).

### `format_time_zone_section(entries, top_n=10)`

Returns a Markdown-compatible plain-text block.  Authors are sorted
alphabetically and capped at `top_n`.  When an author has been seen in more
than one offset the extra offsets appear in parentheses.

## Example output

```
## Time Zone Overview

  Alice: +0200  (also seen: -0500)
  Bob: -0500
  Carol: +0530
```

## Notes

- Both `+HH:MM` and `+HHMM` offset formats are handled; all values are
  normalised to `+HHMM` internally.
- The report is purely informational — no filtering is applied based on
  time zone.
