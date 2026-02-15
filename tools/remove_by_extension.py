#!/usr/bin/env python3
"""Remove files in a directory that match a list of extensions.

Usage:
  python remove_by_extension.py /path/to/dir .tmp .bak .DS_Store [--dry-run]

Notes:
  - Extensions are matched case-insensitively.
  - Leading dots are optional ("tmp" == ".tmp").
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, List, Set


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_file():
                yield path


def normalize_extensions(exts: List[str]) -> Set[str]:
    normalized = set()
    for ext in exts:
        ext = ext.strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = "." + ext
        normalized.add(ext.lower())
    return normalized


def remove_matching_files(root: Path, extensions: Set[str], dry_run: bool) -> int:
    removed = 0
    for path in iter_files(root):
        if path.suffix.lower() in extensions:
            if dry_run:
                print(f"[dry-run] remove {path}")
            else:
                os.remove(path)
                print(f"removed {path}")
            removed += 1
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove files that match a list of extensions.")
    parser.add_argument("dir", type=Path, help="Directory to scan")
    parser.add_argument("extensions", nargs="+", help="Extensions to remove")
    parser.add_argument("--dry-run", action="store_true", help="Print files that would be removed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dir.is_dir():
        raise SystemExit(f"dir is not a directory: {args.dir}")

    extensions = normalize_extensions(args.extensions)
    print(extensions)
    if not extensions:
        raise SystemExit("No valid extensions provided.")

    removed = remove_matching_files(args.dir, extensions, args.dry_run)
    print(f"Done. Removed {removed} files.")


if __name__ == "__main__":
    main()
