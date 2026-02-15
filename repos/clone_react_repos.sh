#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST_FILE="$ROOT_DIR/ReAct repos.md"

if [[ ! -f "$LIST_FILE" ]]; then
  echo "Missing $LIST_FILE" >&2
  exit 1
fi

# Parse markdown bullet links: * [org/**repo**](url)
while IFS= read -r line; do
  [[ "$line" == \*\[*\]\(*\)* ]] || continue

  # Extract URL inside parentheses.
  url="${line#*\(}"
  url="${url%\)}"

  # Extract repo name between ** **.
  repo="${line#*\*\*}"
  repo="${repo%%\*\**}"

  if [[ -z "$repo" || -z "$url" ]]; then
    continue
  fi

  target="$ROOT_DIR/$repo"
  if [[ -d "$target/.git" ]]; then
    echo "Skipping $repo (already cloned)"
    continue
  fi

  echo "Cloning $repo from $url"
  git clone "$url" "$target"
done < "$LIST_FILE"
