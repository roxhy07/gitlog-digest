# Bot / Automated Commit Report

The **bot report** identifies commits made by automated tools such as
Dependabot, Renovate, GitHub Actions, and similar CI bots. It helps teams
quickly understand how much of their weekly activity was human-driven versus
automated dependency management or CI tasks.

## Detection Logic

An author is classified as a bot when their name contains any of the following
patterns (case-insensitive):

| Pattern | Example match |
|---|---|
| `[bot]` | `dependabot[bot]` |
| `-bot` / `bot-` | `renovate-bot`, `bot-runner` |
| `dependabot` | `dependabot` |
| `renovate` | `renovate` |
| `github-actions` | `github-actions[bot]` |
| `snyk-bot` | `snyk-bot` |
| `automation` | `automation-service` |
| `ci-` / `-ci` | `ci-runner`, `deploy-ci` |

## CLI Flags

```
--bots            Include the bot-commit section in the digest output.
--top-bots N      Show the top N bot authors (default: 5).
```

## Example Output

```
Bot / Automated Commits
------------------------
  dependabot[bot]: 8 commit(s)
    - bump requests from 2.28.0 to 2.31.0
    - bump pytest from 7.2.0 to 7.4.0
    - bump black from 23.1.0 to 23.7.0
    ... and 5 more
  renovate-bot: 3 commit(s)
    - update eslint to v8
    - pin node version
    - update lockfile
```

## Programmatic Usage

```python
from gitlog_digest.bot_report import build_bot_map, format_bot_section

bot_map = build_bot_map(commits)
print(format_bot_section(bot_map, n=5))
```

## Summary Line

A compact one-liner is available for digest headers:

```python
from gitlog_digest.bot_cli import bot_summary_line

print(bot_summary_line(commits))
# 11 automated commits from 2 bot account(s)
```
