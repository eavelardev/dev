#!/usr/bin/env python3
"""Remove duplicate files, keeping the shortest path in each duplicate set.

Usage:
  python remove_duplicates_shortest.py /path/to/dir [--workers N] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


READ_SIZE = 1024 * 1024  # 1 MiB


def iter_files(root: Path, skip_dirs: Iterable[str]) -> Iterable[Path]:
    skip_set = {name for name in skip_dirs if name}
    for dirpath, dirnames, filenames in os.walk(root):
        if skip_set:
            dirnames[:] = [name for name in dirnames if name not in skip_set]
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


def select_keep_shortest(paths: List[str]) -> Tuple[str, List[str]]:
    sorted_paths = sorted(paths, key=lambda p: (len(p), p))
    keep = sorted_paths[0]
    remove = sorted_paths[1:]
    return keep, remove


def remove_duplicates(index: Dict[str, List[str]], dry_run: bool) -> int:
    removed = 0
    for paths in index.values():
        if len(paths) <= 1:
            continue
        keep, remove_paths = select_keep_shortest(paths)
        for path in remove_paths:
            if dry_run:
                print(f"[dry-run] remove {path} (kept {keep})")
            else:
                os.remove(path)
                print(f"removed {path} (kept {keep})")
            removed += 1
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove duplicate files within dir, keeping the shortest path per checksum."
    )
    parser.add_argument("dir", type=Path, help="Directory to de-duplicate")
    parser.add_argument(
        "--skip-dir",
        action="append",
        default=[],
        help="Directory name to skip (repeatable)",
    )
    parser.add_argument("--workers", type=int, default=0, help="Worker processes (0=auto, 1=single process)")
    parser.add_argument("--dry-run", action="store_true", help="Print files that would be removed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dir.is_dir():
        raise SystemExit(f"dir is not a directory: {args.dir}")

    workers = args.workers
    if workers == 0:
        workers = max(os.cpu_count() or 1, 1)

    paths = list(iter_files(args.dir, args.skip_dir))

    print(f"Indexing {len(paths)} files in {args.dir}")
    index = build_checksum_index(paths, workers)

    removed = remove_duplicates(index, args.dry_run)
    print(f"Done. Removed {removed} files.")


if __name__ == "__main__":
    main()
