# Ribbon Report

The ribbon report assigns achievement badges to contributors based on their activity within the digest period.

## Overview

Each contributor receives one or more badges depending on metrics such as commit volume, files touched, and net lines changed. Badges provide a quick, human-friendly snapshot of each person's contribution style.

## Badges

| Badge | Criteria |
|---|---|
| **Prolific Committer** | 50 or more commits in the period |
| **Active Contributor** | 10 or more commits in the period |
| **File Wrangler** | 100 or more unique files changed |
| **Code Grower** | Net +1 000 or more lines added |
| **Code Trimmer** | Net −500 or more lines removed |
| **First Step** | Exactly 1 commit in the period |
| **Participant** | Default badge when no other criteria are met |

A contributor can earn multiple badges simultaneously.

## CLI Usage

Add `--ribbons` to any `gitlog-digest` invocation:

```bash
gitlog-digest --ribbons
gitlog-digest --ribbons --top-ribbons 5
```

`--top-ribbons N` limits the ribbon section to the top N contributors (sorted by number of badges earned, descending). Default is 10.

## Output Example

```
### 🎖 Contributor Ribbons

- **alice**: [Prolific Committer]  [Code Grower]
- **bob**: [Active Contributor]  [File Wrangler]
- **carol**: [Participant]
```

## Programmatic API

```python
from gitlog_digest.ribbon_report import build_ribbon_map, format_ribbon_section

ribbon_map = build_ribbon_map(commits)
print(format_ribbon_section(ribbon_map, top_n=5))
```

`build_ribbon_map` returns a `dict[str, RibbonEntry]` keyed by author name.
