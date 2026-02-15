#!/usr/bin/env python3
"""Remove duplicate files in a second directory based on checksum matches.

Usage:
  python remove_duplicates.py /path/to/dir1 /path/to/dir2 [--workers N] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


READ_SIZE = 1024 * 1024  # 1 MiB


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_file():
                yield path


def file_checksum(path: Path) -> Tuple[str, str]:
    # blake2b is fast and in the standard library
    hasher = hashlib.blake2b(digest_size=16)
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(READ_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest(), str(path)


def build_checksum_index(paths: Iterable[Path], workers: int) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    if workers <= 1:
        for path in paths:
            digest, name = file_checksum(path)
            index.setdefault(digest, []).append(name)
        return index

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(file_checksum, path) for path in paths]
        for future in as_completed(futures):
            digest, name = future.result()
            index.setdefault(digest, []).append(name)
    return index


def remove_duplicates(index_a: Dict[str, List[str]], index_b: Dict[str, List[str]], dry_run: bool) -> int:
    common = set(index_a.keys()) & set(index_b.keys())
    removed = 0
    for digest in common:
        for path in index_b[digest]:
            if dry_run:
                print(f"[dry-run] remove {path}")
            else:
                os.remove(path)
                print(f"removed {path}")
            removed += 1
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove files in dir2 that also exist in dir1 based on checksum.")
    parser.add_argument("dir1", type=Path, help="First directory (reference)")
    parser.add_argument("dir2", type=Path, help="Second directory (files removed here)")
    parser.add_argument("--workers", type=int, default=0, help="Worker processes (0=auto, 1=single process)")
    parser.add_argument("--dry-run", action="store_true", help="Print files that would be removed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dir1.is_dir():
        raise SystemExit(f"dir1 is not a directory: {args.dir1}")
    if not args.dir2.is_dir():
        raise SystemExit(f"dir2 is not a directory: {args.dir2}")

    workers = args.workers
    if workers == 0:
        workers = max(os.cpu_count() or 1, 1)

    paths_a = list(iter_files(args.dir1))
    paths_b = list(iter_files(args.dir2))

    print(f"Indexing {len(paths_a)} files in {args.dir1}")
    index_a = build_checksum_index(paths_a, workers)

    print(f"Indexing {len(paths_b)} files in {args.dir2}")
    index_b = build_checksum_index(paths_b, workers)

    removed = remove_duplicates(index_a, index_b, args.dry_run)
    print(f"Done. Removed {removed} files.")


if __name__ == "__main__":
    main()
