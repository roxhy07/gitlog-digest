# Caching

`gitlog-digest` caches parsed git log results on disk to speed up repeated
runs against the same repository and date range.

## How it works

When you run `gitlog-digest`, the tool checks for a cached result keyed by:

- Absolute path of the repository
- `--since` date
- `--until` date

If a fresh cache entry exists (default TTL: **5 minutes**) the git subprocess
is skipped entirely and the cached commits are used directly.

## Cache location

By default cache files are stored in:

```
~/.cache/gitlog-digest/
```

Each entry is a small JSON file named after a 16-character SHA-256 prefix of
the cache key.

## Cache sub-commands

### Show cache status

```bash
gitlog-digest cache status
```

Prints the cache directory path, number of cached entries, and total disk
usage.

### Clear the cache

```bash
gitlog-digest cache clear
```

Deletes all cached JSON files. Useful when you want to force a fresh fetch.

You can point either command at a custom directory:

```bash
gitlog-digest cache clear --dir /tmp/my-cache
```

## Disabling the cache

Pass `--no-cache` (not yet implemented) or simply `clear` before running to
ensure a cold fetch.

## TTL configuration

The TTL is currently hard-coded to 300 seconds. A future release will expose
this via `pyproject.toml` / `.gitlog-digest.toml` under:

```toml
[cache]
ttl_seconds = 300
```
