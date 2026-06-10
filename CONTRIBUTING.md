# Contributing to BT Bridge Templates

Thank you for helping grow the BT Bridge device catalog! Contributing a template means teaching
BT Bridge how to recognize a Bluetooth Low Energy (BLE) device and decode its data. **You do not
need to write any code** — a template is a JSON file describing byte layouts.

This guide assumes no prior experience with this project. If anything is unclear, open a
discussion or issue and we'll help.

## Table of contents

1. [Before you start](#1-before-you-start)
2. [Two ways to author a template](#2-two-ways-to-author-a-template)
3. [Namespaces: `builtin.` vs `contrib.`](#3-namespaces-builtin-vs-contrib)
4. [Step-by-step: add a community template](#4-step-by-step-add-a-community-template)
5. [Validation and lint](#5-validation-and-lint)
6. [Pull request checklist](#6-pull-request-checklist)
7. [Versioning your template](#7-versioning-your-template)
8. [Code of Conduct & licensing](#8-code-of-conduct--licensing)

---

## 1. Before you start

You'll need:

- The device's **GATT layout** — its service and characteristic UUIDs. The BT Bridge agent's
  **GATT analyser** shows these for any connected device, and the broker's **RE (reverse
  engineering) capture** workflow records sample payloads and suggests a field layout. Start
  there — you don't have to reverse-engineer by hand.
- The **byte meaning** of at least one characteristic (which bytes are wind speed, temperature,
  a status flag, etc.) and how to convert raw bytes to a human value (scale/offset, bitmask, enum).

You do **not** need:

- A development environment, a compiler, or the ability to read Kotlin/Python. Templates are pure
  data validated by an automated lint that runs on every pull request.

## 2. Two ways to author a template

1. **By hand** — copy an existing template in `catalog/community/` as a starting point and edit
   the JSON. Good when you already know the byte layout.
2. **From an RE capture** — use the BT Bridge broker's RE workflow to capture live payloads, then
   export a *scaffold* template (`POST /v1/re/session/scaffold`). The scaffold is a valid draft
   `display` template with auto-detected field offsets and `_re_hint` notes; refine it and submit.

Either way, the result is a JSON file in `catalog/community/`.

## 3. Namespaces: `builtin.` vs `contrib.`

Every template ID is `<namespace>.<name>` (e.g. `contrib.acme-thermometer-display`).

| Namespace | Who maintains it | Lives in | Community PRs may modify? |
|---|---|---|---|
| `builtin.` | The BT Bridge project (first-party) | `catalog/builtin/` | **No** |
| `contrib.` | The community | `catalog/community/` | **Yes** |

**Community contributions must use the `contrib.` namespace and go in `catalog/community/`.** The
CI lint rejects any PR that adds or modifies a `builtin.` template unless it's from a maintainer.
This keeps the first-party set stable and clearly separated from community content.

Choose a `contrib.` name that includes the manufacturer and model, e.g.
`contrib.kestrel-5700-display`. Use lowercase, hyphens, no spaces.

## 4. Step-by-step: add a community template

1. **Fork** this repository and create a branch: `git checkout -b add-acme-thermometer`.
2. **Create your template file** under `catalog/community/`. A minimal `display` template:

   ```json
   {
     "schema_version": 1,
     "id": "contrib.acme-thermometer-display",
     "version": "1.0.0",
     "type": "display",
     "name": "Acme Thermometer Display",
     "author": "your-github-handle",
     "default_view": "metric",
     "notifications": [
       {
         "char": "0000fff1-0000-1000-8000-00805f9b34fb",
         "description": "Temperature notification frame",
         "views": {
           "metric": {
             "fields": [
               {
                 "id": "temp_c",
                 "label": "Temperature",
                 "type": "scale_offset",
                 "offset": 0,
                 "length": 2,
                 "encoding": "int16_le",
                 "scale": 0.01,
                 "offset_value": 0.0,
                 "unit": "°C",
                 "precision": 1,
                 "display": true
               }
             ]
           }
         }
       }
     ],
     "reads": []
   }
   ```

3. **Validate locally** (see §5).
4. **Regenerate the catalog index** so your template appears to clients:
   `python3 tools/build_index.py` (commit the updated `catalog/index.json`).
5. **Commit** with a Conventional Commit message:
   `git commit -m "feat(community): add Acme Thermometer display template"`.
6. **Open a pull request.** CI runs the lint and schema validation automatically.

> See [`docs/TEMPLATE_FORMAT.md`](docs/TEMPLATE_FORMAT.md) for the full field-type reference
> (`raw`, `scale_offset`, `bitmask`, `enum`, `expr`, `formula`) and every supported encoding.

## 5. Validation and lint

Before opening a PR, run the lint locally:

```bash
python3 tools/lint_templates.py catalog/ --community-pr
```

`--community-pr` enforces the `contrib.`-only rule. The lint checks:

- Valid JSON and a supported `schema_version`.
- Required `id` and `version`, and that `version` is valid semver.
- No duplicate `(id, version)` pairs.
- All `requires` dependencies resolve to an installed version.
- Community PRs touch only `contrib.` templates.

A clean run prints `OK: catalog/ — no errors` and exits 0.

## 6. Pull request checklist

- [ ] Template ID uses the `contrib.` namespace.
- [ ] File is under `catalog/community/`.
- [ ] `python3 tools/lint_templates.py catalog/ --community-pr` passes.
- [ ] `catalog/index.json` regenerated and committed.
- [ ] `author` field set to your GitHub handle (or org).
- [ ] If decoding is unverified against real hardware, say so in the PR description.

## 7. Versioning your template

Use [semantic versioning](https://semver.org): `MAJOR.MINOR.PATCH`.

- **PATCH** — fix a wrong scale/offset, typo in a label.
- **MINOR** — add a new view or field without breaking existing ones.
- **MAJOR** — change field IDs/offsets in a way that breaks consumers.

Never edit a published version in place if it changes behavior — publish a new version. The
catalog keeps multiple versions side by side.

Per-template versions are independent of the catalog *repository* version. For the repo-level
release policy (tags, the `schema_version` vs template-version distinction, and the release flow),
see [`docs/VERSIONING.md`](docs/VERSIONING.md). Tooling/schema changes are noted in
[`CHANGELOG.md`](CHANGELOG.md); to report a security issue see [`SECURITY.md`](SECURITY.md).

## 8. Code of Conduct & licensing

By contributing, you agree that your contribution is licensed under
[Apache-2.0](LICENSE), and you agree to abide by our
[Code of Conduct](CODE_OF_CONDUCT.md). Your `author` attribution is retained in the template file.
