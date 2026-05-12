# Git Hook Integration

`gitlog-digest` can install a **post-commit hook** into any local repository.
Whenever a new commit is created the hook automatically clears the local digest
cache, so the next `gitlog-digest` run always reflects the latest history.

## Installing the hook

```bash
# From inside your repository
gitlog-digest hooks install

# Or point at a specific repo
gitlog-digest hooks install --repo /path/to/repo
```

If a `post-commit` hook already exists, gitlog-digest **appends** its lines
rather than overwriting your existing hook.

## Checking hook status

```bash
gitlog-digest hooks status
```

Outputs either `installed` or `not installed` for the target repository.

## Removing the hook

```bash
gitlog-digest hooks uninstall
```

Only the lines added by gitlog-digest are removed.  Any pre-existing hook
content is preserved.

## What the hook does

The installed snippet is intentionally minimal:

```sh
#!/bin/sh
# Installed by gitlog-digest — clears digest cache on new commits.
if command -v gitlog-digest > /dev/null 2>&1; then
    gitlog-digest cache clear --quiet 2>/dev/null || true
fi
```

- It only runs when `gitlog-digest` is available on `PATH`.
- Failures are silenced so they never block a commit.
- No network access or heavy processing is performed.

## Programmatic usage

The underlying helpers live in `gitlog_digest.hooks`:

```python
from gitlog_digest.hooks import install_hook, uninstall_hook, is_installed

install_hook("/path/to/repo")   # idempotent
is_installed("/path/to/repo")   # True / False
uninstall_hook("/path/to/repo") # returns True if anything changed
```
