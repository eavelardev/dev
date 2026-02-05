#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


TAG_ORDER = ["cloud", "embedding", "vision", "tools", "thinking"]


def main() -> int:
    here = Path(__file__).resolve().parent
    json_path = here / "models_data.json"
    csv_path = here / "models.csv"

    data = json.loads(json_path.read_text(encoding="utf-8"))
    models = data["models"]

    # Determine tag columns from per-version tags (keep canonical order first)
    tags_found: set[str] = set()
    for m in models:
        for v in m.get("versions", []):
            for t in v.get("tags", []):
                tags_found.add(str(t))

    tag_columns = [t for t in TAG_ORDER if t in tags_found]
    tag_columns.extend(sorted(tags_found - set(tag_columns)))

    fieldnames = [
        "idx",
        "select",
        "provider",
        "model_name",
        "model_version",
        "version_aliases",
        "latest",
        "param_size",
        "size_gb",
        "context",
        *tag_columns,
        "hybrid",
        "RAG",
        "link",
        "date",
        "description",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        model_idx = 1

        for m in models:
            provider = m["provider"]
            model_name = m["model_name"]
            description = m["description"]

            model_has_think_and_instruct = (
                any("thinking" in {t for t in v["tags"]} for v in m["versions"])
                and any("instruct" in {t for t in v["tags"]} for v in m["versions"])
            )

            versions = sorted(
                m["versions"],
                key=lambda v: v["model_version"],
            )

            grouped: dict[str, list[dict]] = {}
            for v in versions:
                model_version_full = v["model_version"]
                hash_value = v["hash"]
                group_key = hash_value or f"nohash:{model_version_full}"
                grouped.setdefault(group_key, []).append(v)

            for group_versions in grouped.values():
                names = [v["model_version"] for v in group_versions]
                names_sorted = sorted(names, key=lambda n: (len(n), n))
                chosen_full = names_sorted[0] if names_sorted else ""
                aliases = [n for n in names_sorted[1:] if n]
                alias_versions = [a.split(":", 1)[1] if ":" in a else a for a in aliases]

                chosen = next((v for v in group_versions if v["model_version"] == chosen_full), group_versions[0])

                url = chosen.get("version_link", "")
                sheet_link = f'=HYPERLINK("{url}", "link")' if url else ""

                size_gb = chosen.get("size_gb", None)
                size_gb = None if size_gb is None else round(size_gb, 2)

                tags = set(t for t in chosen.get("tags", []))

                param_size = str(chosen.get("param_size", "") or "")

                if ":" in chosen_full:
                    model_version = chosen_full.split(":", 1)[1]
                else:
                    model_version = ""

                select_providers = ["Google", "IBM", "Meta", "Microsoft", "NVIDIA", "OpenAI", "Mistral", "Moonshot AI"]

                row = {
                    "idx": model_idx,
                    "select": "select" if provider in select_providers or model_name.startswith("qwen3") else None,
                    "provider": provider,
                    "model_name": model_name,
                    "model_version": model_version,
                    "version_aliases": ", ".join(alias_versions),
                    "latest": "latest" if model_version == "latest" or "latest" in alias_versions else None,
                    "param_size": param_size,
                    "size_gb": size_gb,
                    "context": chosen.get("context_display", ""),
                    "hybrid": "hybrid" if model_has_think_and_instruct else None,
                    "RAG": "RAG" if "RAG" in description else None,
                    "link": sheet_link,
                    "date": chosen.get("updated", ""),
                    "description": description,
                }

                for t in tag_columns:
                    row[t] = t if t in tags else None

                w.writerow(row)
                model_idx += 1

    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
