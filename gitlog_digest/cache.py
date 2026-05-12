"""Simple file-based cache for git log results to avoid re-parsing unchanged repos."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "gitlog-digest"
DEFAULT_TTL_SECONDS = 300  # 5 minutes


def _cache_key(repo: str, since: str, until: str) -> str:
    """Generate a stable cache key from query parameters."""
    raw = f"{os.path.abspath(repo)}|{since}|{until}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_path(key: str, cache_dir: Path) -> Path:
    return cache_dir / f"{key}.json"


def load_cache(
    repo: str,
    since: str,
    until: str,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    ttl: int = DEFAULT_TTL_SECONDS,
) -> Optional[list]:
    """Return cached commit data if fresh, else None."""
    key = _cache_key(repo, since, until)
    path = _cache_path(key, cache_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data["timestamp"] > ttl:
            return None
        return data["commits"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def save_cache(
    repo: str,
    since: str,
    until: str,
    commits: list,
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> None:
    """Persist commit data to disk cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(repo, since, until)
    path = _cache_path(key, cache_dir)
    payload = {"timestamp": time.time(), "commits": commits}
    path.write_text(json.dumps(payload, indent=2))


def clear_cache(cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    """Delete all cache files. Returns number of files removed."""
    if not cache_dir.exists():
        return 0
    removed = 0
    for p in cache_dir.glob("*.json"):
        p.unlink()
        removed += 1
    return removed
