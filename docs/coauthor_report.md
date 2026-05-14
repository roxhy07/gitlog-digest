# Co-author Report

The co-author report surfaces collaboration patterns hidden inside commit
trailers.  Many teams use the `Co-authored-by:` convention (popularised by
GitHub) to credit pair-programming partners or reviewers who contributed
directly to a change.

## How it works

For every commit in the selected date range, `gitlog_digest` scans the commit
body for lines that match:

```
Co-authored-by: Name <email>
```

The match is **case-insensitive**, so `CO-AUTHORED-BY:` and
`co-authored-by:` are both recognised.  Each such trailer is treated as a
*(driver, navigator)* pair where the primary commit author is the driver.

Pairs are accumulated across all commits and ranked by frequency.

## CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--coauthors` | off | Enable the co-author section in the digest |
| `--coauthors-top-n N` | 10 | Show only the top *N* pairs |

### Example

```bash
gitlog-digest --coauthors --coauthors-top-n 5
```

Sample output:

```
### Co-author Pairs

  Alice + Bob: 12 commit(s)
  Carol + Dave: 7 commit(s)
  Alice + Carol: 3 commit(s)
```

## Programmatic usage

```python
from gitlog_digest.coauthor_report import build_coauthor_map, top_pairs, format_coauthor_section

pair_map = build_coauthor_map(commits)
pairs    = top_pairs(pair_map, n=5)
print(format_coauthor_section(pairs))
```

## Notes

- Only the **name** portion of the trailer is extracted; email addresses are
  stripped.
- Pairs are **directional**: `(Alice, Bob)` and `(Bob, Alice)` are counted
  separately because the commit author (driver) is distinct from the
  co-author (navigator).
- Commits without a body are silently skipped.
