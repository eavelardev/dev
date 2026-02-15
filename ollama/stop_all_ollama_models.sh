#!/usr/bin/env bash
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama not found in PATH" >&2
  exit 1
fi

mapfile -t models < <(ollama ps 2>/dev/null | awk 'NR>1 {print $1}' | sort -u)

if [[ ${#models[@]} -eq 0 ]]; then
  echo "No running models found."
  exit 0
fi

for model in "${models[@]}"; do
  if [[ -n "$model" ]]; then
    echo "Stopping $model"
    ollama stop "$model" || echo "Failed to stop $model" >&2
  fi
done
