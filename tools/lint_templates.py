#!/usr/bin/env python3
"""CI lint for BT Bridge template files.

Validates JSON, schema_version, required fields, semver, duplicates, dependency
resolvability, and (with --community-pr) the contrib.-only namespace rule.

Usage:
    python3 tools/lint_templates.py [catalog_dir] [--community-pr]

Exit code 0 = clean. Exit code 1 = errors found.

This is the same validation the BT Bridge broker applies at load time, packaged here so the
catalog repository can gate contributions in CI before they are ever published to the index.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any

from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier

SUPPORTED_SCHEMA_VERSIONS = {1}
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG_DIR = REPO_ROOT / "catalog"
INDEX_NAME = "index.json"


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def lint_directory(directory: pathlib.Path, is_community_pr: bool = False) -> LintResult:
    result = LintResult()
    seen: dict[tuple[str, str], pathlib.Path] = {}
    templates: list[dict[str, Any]] = []

    for path in sorted(directory.rglob("*.json")):
        if path.name == INDEX_NAME:
            continue  # the generated index is not a template
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            result.errors.append(f"{path}: JSON parse error: {exc}")
            continue

        if not isinstance(data, dict):
            result.errors.append(f"{path}: top-level JSON is not an object")
            continue

        schema_ver = data.get("schema_version")
        if schema_ver not in SUPPORTED_SCHEMA_VERSIONS:
            result.errors.append(
                f"{path}: unsupported schema_version={schema_ver!r} "
                f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
            )
            continue

        tid = data.get("id")
        ver = data.get("version")
        if not tid:
            result.errors.append(f"{path}: missing required field 'id'")
            continue
        if not ver:
            result.errors.append(f"{path}: missing required field 'version'")
            continue

        try:
            Version(ver)
        except InvalidVersion:
            result.errors.append(f"{path}: invalid semver version {ver!r}")
            continue

        if is_community_pr and tid.startswith("builtin."):
            result.errors.append(
                f"{path}: community PRs may not add or modify builtin. templates "
                f"(use the contrib. namespace under catalog/community/)"
            )

        # Community templates should live under catalog/community/
        if tid.startswith("contrib.") and "community" not in path.parts:
            result.warnings.append(
                f"{path}: contrib. template not under catalog/community/"
            )

        key = (tid, ver)
        if key in seen:
            result.errors.append(
                f"Duplicate template ({tid}, {ver}): {path} conflicts with {seen[key]}"
            )
        else:
            seen[key] = path
            templates.append(data)

    # Resolve all requires entries against the installed set.
    all_ids: dict[str, list[str]] = {}
    for t in templates:
        all_ids.setdefault(t["id"], []).append(t["version"])

    for t in templates:
        tid, ver = t["id"], t["version"]
        for dep_id, spec_str in t.get("requires", {}).items():
            try:
                spec = SpecifierSet(spec_str, prereleases=True)
            except InvalidSpecifier:
                result.errors.append(
                    f"{tid}@{ver}: invalid requires specifier for {dep_id}: {spec_str!r}"
                )
                continue
            dep_versions = all_ids.get(dep_id, [])
            candidates = [v for v in dep_versions if Version(v) in spec]
            if not candidates:
                result.errors.append(
                    f"{tid}@{ver}: unresolvable requires {dep_id}@{spec_str} "
                    f"(installed versions: {dep_versions or 'none'})"
                )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="BT Bridge template CI lint")
    parser.add_argument("directory", nargs="?", default=str(CATALOG_DIR))
    parser.add_argument("--community-pr", action="store_true")
    args = parser.parse_args()

    directory = pathlib.Path(args.directory)
    if not directory.exists():
        print(f"ERROR: directory not found: {directory}")
        sys.exit(1)

    result = lint_directory(directory, is_community_pr=args.community_pr)

    for w in result.warnings:
        print(f"WARN:  {w}")
    for e in result.errors:
        print(f"ERROR: {e}")

    if result.ok:
        print(f"OK: {directory} — no errors")
        sys.exit(0)
    print(f"FAIL: {len(result.errors)} error(s)")
    sys.exit(1)


if __name__ == "__main__":
    main()
