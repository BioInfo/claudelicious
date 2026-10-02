#!/usr/bin/env python3
"""Artificial Analysis API CLI wrapper.

Usage:
  aa.py llms                          # all LLMs (full table)
  aa.py llms --slugs gpt-5-5,claude-opus-5-5
  aa.py llms --creator anthropic
  aa.py llms --top intelligence 10    # top N by intelligence|coding|math|speed|tps|cheap
  aa.py llms --raw                    # raw JSON dump
  aa.py text-to-image
  aa.py image-editing
  aa.py text-to-speech
  aa.py text-to-video
  aa.py image-to-video

Auth: reads API key from `pass api-keys/artificialanalysis`.
Cache: ~/.cache/artificial-analysis/<endpoint>.json (1h TTL).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://artificialanalysis.ai/api/v2"
CACHE_DIR = Path.home() / ".cache" / "artificial-analysis"
CACHE_TTL = 3600  # 1 hour

ENDPOINTS = {
    "llms": "/data/llms/models",
    "text-to-image": "/data/media/text-to-image",
    "image-editing": "/data/media/image-editing",
    "text-to-speech": "/data/media/text-to-speech",
    "text-to-video": "/data/media/text-to-video",
    "image-to-video": "/data/media/image-to-video",
}


def get_key() -> str:
    """Read API key from env (AA_API_KEY) or `pass api-keys/artificialanalysis`."""
    if env := os.environ.get("AA_API_KEY"):
        return env.strip()
    try:
        out = subprocess.run(
            ["pass", "api-keys/artificialanalysis"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(
            "error: no API key. Set AA_API_KEY env var, "
            "or store in `pass api-keys/artificialanalysis`."
        )


def fetch(endpoint: str, force: bool = False) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{endpoint}.json"
    if not force and cache.exists() and (time.time() - cache.stat().st_mtime) < CACHE_TTL:
        return json.loads(cache.read_text())
    url = BASE + ENDPOINTS[endpoint]
    req = urllib.request.Request(url, headers={"x-api-key": get_key()})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    cache.write_text(json.dumps(data))
    return data


def fmt_llms(rows: list[dict]) -> str:
    cols = ("name", "creator", "intel", "code", "math", "tps", "ttft", "$/1M(blend)")
    out = ["\t".join(cols)]
    for m in rows:
        ev = m.get("evaluations") or {}
        pr = m.get("pricing") or {}
        out.append("\t".join([
            m.get("name", ""),
            (m.get("model_creator") or {}).get("name", ""),
            f"{ev.get('artificial_analysis_intelligence_index') or '-'}",
            f"{ev.get('artificial_analysis_coding_index') or '-'}",
            f"{ev.get('artificial_analysis_math_index') or '-'}",
            f"{m.get('median_output_tokens_per_second') or '-'}",
            f"{m.get('median_time_to_first_token_seconds') or '-'}",
            f"{pr.get('price_1m_blended_3_to_1') or '-'}",
        ]))
    return "\n".join(out)


def filter_llms(data: list[dict], args) -> list[dict]:
    rows = data
    if args.slugs:
        wanted = {s.strip().lower() for s in args.slugs.split(",")}
        rows = [m for m in rows if m.get("slug", "").lower() in wanted
                or m.get("name", "").lower() in wanted]
    if args.creator:
        c = args.creator.lower()
        rows = [m for m in rows if c in (m.get("model_creator") or {}).get("slug", "").lower()
                or c in (m.get("model_creator") or {}).get("name", "").lower()]
    if args.search:
        q = args.search.lower()
        rows = [m for m in rows if q in m.get("name", "").lower() or q in m.get("slug", "").lower()]
    if args.top:
        metric, n = args.top
        n = int(n)
        keymap = {
            "intelligence": lambda m: (m.get("evaluations") or {}).get("artificial_analysis_intelligence_index") or -1,
            "coding": lambda m: (m.get("evaluations") or {}).get("artificial_analysis_coding_index") or -1,
            "math": lambda m: (m.get("evaluations") or {}).get("artificial_analysis_math_index") or -1,
            "tps": lambda m: m.get("median_output_tokens_per_second") or -1,
            "speed": lambda m: m.get("median_output_tokens_per_second") or -1,
            "cheap": lambda m: -((m.get("pricing") or {}).get("price_1m_blended_3_to_1") or 1e9),
        }
        if metric not in keymap:
            sys.exit(f"unknown --top metric: {metric}. options: {list(keymap)}")
        rows = sorted(rows, key=keymap[metric], reverse=True)[:n]
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("endpoint", choices=list(ENDPOINTS))
    p.add_argument("--raw", action="store_true", help="raw JSON")
    p.add_argument("--refresh", action="store_true", help="bypass cache")
    p.add_argument("--slugs", help="comma list of slugs/names to filter")
    p.add_argument("--creator", help="filter by creator (e.g. anthropic, openai, google)")
    p.add_argument("--search", help="substring match on name/slug")
    p.add_argument("--top", nargs=2, metavar=("METRIC", "N"),
                   help="top N by intelligence|coding|math|speed|tps|cheap")
    args = p.parse_args()

    payload = fetch(args.endpoint, force=args.refresh)
    data = payload.get("data", payload)

    if args.raw:
        if args.endpoint == "llms":
            data = filter_llms(data, args)
        print(json.dumps(data, indent=2))
        return

    if args.endpoint == "llms":
        data = filter_llms(data, args)
        print(fmt_llms(data))
    else:
        # media endpoints: print name + elo
        for m in data:
            name = m.get("name") or m.get("model_name") or m.get("slug", "?")
            elo = m.get("elo") or m.get("elo_rating") or m.get("rating") or "-"
            print(f"{name}\t{elo}")


if __name__ == "__main__":
    main()
