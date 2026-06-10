# Changelog

All notable changes to the `bt-bridge-templates` catalog (tooling, schema, and CI) are documented
here. Individual template versions are tracked in each template's own `version` field, not in this
changelog (see [`docs/VERSIONING.md`](docs/VERSIONING.md)).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.9.0] — 2026-06-08

First versioned release. Establishes the template catalog: the canonical, versioned home for the
device/display/codec/component templates the BT Bridge broker fetches on demand.

### Added
- **Catalog structure** — `catalog/builtin/` (first-party `builtin.*` templates) and
  `catalog/community/` (community `contrib.*` contributions), with a generated machine-readable
  `catalog/index.json` (id, version, type, path, `sha256`, `requires`) as the client-facing manifest.
- **Built-in templates (schema_version 1):** WeatherFlow Tactical device + display (confirmed
  little-endian protocol, vendor UUIDs); Niimbot label-printer device + UART codec; and shared
  Battery Service and Device Information GATT component templates.
- **Tooling** — `tools/build_index.py` (index generator with a `--check` CI guard) and
  `tools/lint_templates.py` (JSON/schema/semver/duplicate/dependency/namespace lint, caret/tilde-aware,
  consistent with the broker's lint).
- **CI** — `validate.yml`: structural lint over the whole catalog, a `contrib.`-only namespace gate
  for community templates, and an index-freshness check, on every push and PR.
- FOSS scaffolding: Apache-2.0 `LICENSE`/`NOTICE`, `CONTRIBUTING.md` (no-code template authoring
  guide), `CODE_OF_CONDUCT.md`, `docs/TEMPLATE_FORMAT.md`, `docs/VERSIONING.md`, PR + issue templates.

[Unreleased]: https://github.com/ColdBoreBallistics/bt-bridge-templates/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/ColdBoreBallistics/bt-bridge-templates/releases/tag/v0.9.0
