"""CLI sub-commands for cache management (clear, status)."""

import argparse
from pathlib import Path

from gitlog_digest.cache import DEFAULT_CACHE_DIR, clear_cache


def add_cache_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register 'cache' sub-command onto an existing subparsers group."""
    parser = subparsers.add_parser("cache", help="Manage the local digest cache")
    sub = parser.add_subparsers(dest="cache_cmd", required=True)

    clear_p = sub.add_parser("clear", help="Remove all cached results")
    clear_p.add_argument(
        "--dir",
        dest="cache_dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Cache directory (default: %(default)s)",
    )

    status_p = sub.add_parser("status", help="Show cache directory and file count")
    status_p.add_argument(
        "--dir",
        dest="cache_dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Cache directory (default: %(default)s)",
    )

    parser.set_defaults(func=handle_cache_command)


def handle_cache_command(args: argparse.Namespace) -> None:
    cache_dir = Path(args.cache_dir)

    if args.cache_cmd == "clear":
        removed = clear_cache(cache_dir=cache_dir)
        print(f"Removed {removed} cached file(s) from {cache_dir}")

    elif args.cache_cmd == "status":
        if not cache_dir.exists():
            print(f"Cache directory does not exist: {cache_dir}")
            return
        files = list(cache_dir.glob("*.json"))
        total_bytes = sum(f.stat().st_size for f in files)
        print(f"Cache directory : {cache_dir}")
        print(f"Cached entries  : {len(files)}")
        print(f"Total size      : {total_bytes} bytes")
