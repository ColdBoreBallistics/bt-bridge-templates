# Versioning & Release Policy

The BT Bridge project follows [Semantic Versioning 2.0.0](https://semver.org/). This document is
the versioning policy for **`bt-bridge-templates`** (the template catalog); the canonical
cross-project copy lives in
[`bt-bridge-broker/docs/VERSIONING.md`](https://github.com/ColdBoreBallistics/bt-bridge-broker/blob/main/docs/VERSIONING.md).

The catalog has **two distinct version concerns**: the catalog *repository* version, and each
*template's* own version. They are independent.

## 1. Per-template versions (the common case)

Every template carries its own `version` field and is versioned independently with SemVer:

| Component | Increment when |
|---|---|
| **MAJOR** | A breaking change to the template: removing/renaming fields, changing offsets or `id`s in a way that breaks consumers. |
| **MINOR** | Adding a new view or field without breaking existing ones. |
| **PATCH** | Fixing a wrong scale/offset, a label typo, or other non-breaking correction. |

Rules:
- The catalog holds **multiple versions of the same template ID side by side** — never edit a
  published `(id, version)` in place if behavior changes; publish a new version instead.
- `schema_version` (the format-of-the-format integer) is separate from a template's SemVer
  `version`. A `schema_version` bump is a project-wide breaking change (broker MAJOR territory).
- Clients resolve the highest installed version satisfying a dependency's semver range.

A per-template version bump is a normal data PR — it does **not** require a repo release.

## 2. Catalog repository version (releases)

The repository itself is released with `v<version>` tags (matching the project versioning policy)
when the catalog tooling, schema, or CI changes meaningfully — e.g. a `schema_version` bump, a new
`tools/` capability, or an index-format change. Routine template additions/edits do not need a repo
release; they flow continuously to `main` and the regenerated `catalog/index.json`.

### The 0.x pre-release phase

While `0.y.z`, the catalog tooling/schema is not frozen; a `0.MINOR` may include breaking
tooling/schema changes. `1.0.0` marks the stable contract.

## 3. Tags & releases

- **Tag format:** `v<version>`, annotated, from `main` only.
- A release = git tag + GitHub Release (notes from `CHANGELOG.md`); the release may attach/publish
  the generated `catalog/index.json` so clients can pin to a release.
- Published tags are immutable.

## 4. Branching & flow

- `main` is always valid: CI (`validate.yml`) runs the lint + index-freshness check on every PR.
- Template contributions: fork → `contrib.*` template under `catalog/community/` → regenerate
  `catalog/index.json` → reviewed PR → merge. (See `CONTRIBUTING.md`.)
- Tooling/schema changes follow the standard topic-branch → PR → `main` flow, and trigger a repo
  release when they change the contract.

---

*Conforms to the canonical BT Bridge versioning policy in `bt-bridge-broker/docs/VERSIONING.md`.*
