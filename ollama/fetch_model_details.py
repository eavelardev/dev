#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import html as html_lib

# Reuse provider inference + text cleanup
from ollama_models import get_model_urls
from providers import infer_provider


KNOWN_TAGS = ["cloud", "embedding", "thinking", "tools", "vision"]

TAG_RE = re.compile(r">\s*(cloud|embedding|thinking|tools|vision)\s*<", re.IGNORECASE)

MODEL_DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"\s*/?>', re.IGNORECASE)

# Parse the desktop table rows (more structured than the mobile rows).
VERSION_ROW_RE = re.compile(
    r'<div class="hidden group[^>]*sm:grid[^>]*>\s*'
    r'.*?<a href="(?P<href>/library/[^"]+)"[^>]*>(?P<name>[^<]+)</a>'
    r'.*?<p class="col-span-2 text-neutral-500">(?P<size>[^<]+)</p>'
    r'.*?<p class="col-span-2 text-neutral-500">(?P<context>[^<]+)</p>'
    r'.*?<p class="col-span-2 text-neutral-500">\s*(?P<input>[^<]+?)\s*</p>'
    r'.*?</div>',
    re.IGNORECASE | re.DOTALL,
)

PARAM_SIZE_RE = re.compile(r"(e?\d+(?:\.\d+)?[bm]|\d+x\d+b)", re.IGNORECASE)

def _clean_text(text: str) -> str:
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch(url: str, timeout_s: float = 25.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ollama-tag-scraper/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _cache_path(cache_dir: Path, model_name: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", model_name)
    return cache_dir / f"{safe}.html"


def extract_tags_from_page(html: str) -> list[str]:
    snippet = html[:50000]
    found = {m.group(1).lower() for m in TAG_RE.finditer(snippet)}
    return [t for t in KNOWN_TAGS if t in found]


def extract_description_from_page(html: str) -> str:
    m = MODEL_DESC_RE.search(html)
    if not m:
        return ""
    return _clean_text(m.group(1))


def _parse_size(size_text: str) -> float | None:
    s = size_text.strip()
    if not s or s == "-":
        return None
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*(TB|GB|MB)$", s, re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).upper()
    if unit == "MB":
        return val / 1024.0
    if unit == "TB":
        return val * 1024.0
    return val


def _parse_context_tokens(context_text: str) -> int | None:
    s = context_text.strip().upper()
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)([KMG]?)$", s)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    mult = {"": 1, "K": 1_000, "M": 1_000_000, "G": 1_000_000_000}.get(unit)
    if not mult:
        return None
    return int(val * mult)


def extract_param_size_from_version(model_version: str) -> str:
    if ":" not in model_version:
        return ""
    tag = model_version.split(":", 1)[1]
    m = PARAM_SIZE_RE.search(tag)
    if not m:
        return ""
    return m.group(1).lower()


def extract_versions_from_page(html: str, page_tags: list[str]) -> list[dict]:
    versions: list[dict] = []
    seen: set[str] = set()

    for m in VERSION_ROW_RE.finditer(html):
        href = m.group("href")
        name = _clean_text(m.group("name"))
        size_text = _clean_text(m.group("size"))
        context_text = _clean_text(m.group("context"))
        input_text = _clean_text(m.group("input"))

        if name in seen:
            continue
        seen.add(name)

        input_types = [p.strip() for p in input_text.split(",") if p.strip()]

        # Version tags: inherit page tags + infer cloud from the version label.
        version_tags = set(page_tags)
        if ":" in name and "cloud" in name.split(":", 1)[1].lower():
            version_tags.add("cloud")

        versions.append(
            {
                "model_version": name,
                "param_size": extract_param_size_from_version(name),
                "version_href": href,
                "version_link": f"https://ollama.com{href}",
                "size_display": "" if size_text == "-" else size_text,
                "size_gb": _parse_size(size_text),
                "context_display": context_text,
                "context_tokens": _parse_context_tokens(context_text),
                "input": input_types,
                "tags": sorted(version_tags),
            }
        )

    return versions


def main() -> int:
    here = Path(__file__).resolve().parent
    out_json = here / "models_data.json"
    cache_dir = here / ".cache" / "ollama_library"
    cache_dir.mkdir(parents=True, exist_ok=True)

    models_url = get_model_urls()

    models: list[dict] = []
    total_versions = 0

    for idx, url in enumerate(models_url, start=1):
        model_name = url.rsplit("/", 1)[-1]

        cached = _cache_path(cache_dir, model_name)
        if cached.exists():
            page_html = cached.read_text(encoding="utf-8", errors="ignore")
        else:
            print(f"[{idx}/{len(models_url)}] fetch {url}")
            page_html = _fetch(url)
            cached.write_text(page_html, encoding="utf-8")
            time.sleep(0.25)

        description = extract_description_from_page(page_html)
        page_tags = extract_tags_from_page(page_html)
        versions = extract_versions_from_page(page_html, page_tags)
        total_versions += len(versions)

        provider = infer_provider(model_name)

        models.append(
            {
                "provider": provider,
                "model_name": model_name,
                "model_link": url,
                "description": description,
                "page_tags": page_tags,
                "versions": versions,
            }
        )

    dataset = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tag_columns": KNOWN_TAGS,
        "model_count": len(models),
        "model_version_count": total_versions,
        "models": models,
    }

    out_json.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out_json} ({len(models)} models, {total_versions} versions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
