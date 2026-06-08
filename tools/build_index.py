#!/usr/bin/env python3
"""Build catalog/index.json from all template files under catalog/.

The index is the machine-readable manifest that BT Bridge clients (the broker's CLI helper
and web selection page) fetch on demand to discover available templates without cloning the
whole repository. One entry per (id, version), with the metadata needed to display a choice
and the relative path + content hash needed to download and verify the file.

Usage:
    python3 tools/build_index.py            # write catalog/index.json
    python3 tools/build_index.py --check    # exit 1 if index.json is stale (CI guard)

Exit code 0 = success / index up to date. Exit code 1 = error or (with --check) stale index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG_DIR = REPO_ROOT / "catalog"
INDEX_PATH = CATALOG_DIR / "index.json"

# Bump when the index format itself changes (not when templates change).
INDEX_FORMAT_VERSION = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_index() -> dict[str, Any]:
    """Scan catalog/ and return the index dict."""
    entries: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], pathlib.Path] = {}

    for path in sorted(CATALOG_DIR.rglob("*.json")):
        if path == INDEX_PATH:
            continue
        raw = path.read_bytes()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"ERROR: {path} is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

        tid = data.get("id")
        ver = data.get("version")
        if not tid or not ver:
            print(f"ERROR: {path} missing id or version", file=sys.stderr)
            sys.exit(1)

        key = (tid, ver)
        if key in seen:
            print(
                f"ERROR: duplicate ({tid}, {ver}): {path} conflicts with {seen[key]}",
                file=sys.stderr,
            )
            sys.exit(1)
        seen[key] = path

        rel = path.relative_to(REPO_ROOT).as_posix()
        namespace = tid.split(".", 1)[0]
        entries.append(
            {
                "id": tid,
                "version": ver,
                "type": data.get("type"),
                "name": data.get("name"),
                "description": data.get("description"),
                "author": data.get("author"),
                "namespace": namespace,
                "path": rel,
                "sha256": _sha256(raw),
                "requires": data.get("requires", {}),
            }
        )

    entries.sort(key=lambda e: (e["id"], e["version"]))
    return {
        "index_format_version": INDEX_FORMAT_VERSION,
        "count": len(entries),
        "templates": entries,
    }


def _serialize(index: dict[str, Any]) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the BT Bridge templates catalog index.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if catalog/index.json is missing or stale.",
    )
    args = parser.parse_args()

    index = build_index()
    serialized = _serialize(index)

    if args.check:
        if not INDEX_PATH.exists():
            print("ERROR: catalog/index.json does not exist — run build_index.py", file=sys.stderr)
            sys.exit(1)
        current = INDEX_PATH.read_text(encoding="utf-8")
        if current != serialized:
            print(
                "ERROR: catalog/index.json is stale — run 'python3 tools/build_index.py' "
                "and commit the result.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"OK: index up to date ({index['count']} templates).")
        return

    INDEX_PATH.write_text(serialized, encoding="utf-8")
    print(f"Wrote {INDEX_PATH.relative_to(REPO_ROOT)} ({index['count']} templates).")


if __name__ == "__main__":
    main()
