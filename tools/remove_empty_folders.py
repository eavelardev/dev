#!/usr/bin/env python3
"""Remove empty folders from a directory tree.

Usage:
  python remove_empty_folders.py /path/to/root [--dry-run]
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List


def find_empty_dirs(root: Path) -> List[Path]:
    # Walk bottom-up so nested empty folders are removed first.
    empty_dirs: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if dirnames or filenames:
            # Directory is not empty.
            continue
        empty_dirs.append(Path(dirpath))
    return empty_dirs


def remove_empty_dirs(empty_dirs: List[Path], dry_run: bool) -> int:
    removed = 0
    for path in empty_dirs:
        if dry_run:
            print(f"[dry-run] remove {path}")
        else:
            path.rmdir()
            print(f"removed {path}")
        removed += 1
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove empty folders from a directory tree.")
    parser.add_argument("root", type=Path, help="Root directory to clean")
    parser.add_argument("--dry-run", action="store_true", help="Print folders that would be removed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.root.is_dir():
        raise SystemExit(f"root is not a directory: {args.root}")

    empty_dirs = find_empty_dirs(args.root)
    removed = remove_empty_dirs(empty_dirs, args.dry_run)
    print(f"Done. Removed {removed} empty folders.")


if __name__ == "__main__":
    main()
