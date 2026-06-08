# BT Bridge Template Format Reference

This is the authoring reference for template files in this catalog. It covers the four template
types, the display field types, and the supported byte encodings. It assumes no prior experience
with the format — every field is explained.

> The broker and agent implement exactly this format. If a template validates with
> `tools/lint_templates.py` and follows this reference, it will load and render correctly.

## Table of contents

1. [Common fields](#1-common-fields)
2. [Identity and versioning](#2-identity-and-versioning)
3. [Device template](#3-device-template)
4. [Display template](#4-display-template)
5. [Field types](#5-field-types)
6. [Encodings](#6-encodings)
7. [Codec template](#7-codec-template)
8. [Component template](#8-component-template)
9. [Notification matching](#9-notification-matching)

---

## 1. Common fields

Every template, regardless of type, has these top-level fields:

| Field | Required | Meaning |
|---|---|---|
| `schema_version` | yes | Integer format version. Currently `1`. The broker refuses templates with a higher value than it understands. |
| `id` | yes | `<namespace>.<name>` — `builtin.*` (first-party) or `contrib.*` (community). |
| `version` | yes | Semantic version of this template, e.g. `"1.2.0"`. |
| `type` | yes | One of `device`, `display`, `codec`, `component`. |
| `name` | yes | Human-readable display name. |
| `author` | recommended | `"builtin"` or your GitHub handle. |
| `description` | recommended | One-line summary. |
| `requires` | no | Map of `dep_id` → semver range for hard dependencies. |

## 2. Identity and versioning

- IDs are globally unique within the catalog by `(id, version)`.
- The catalog may hold multiple versions of one ID; clients resolve the highest version that
  satisfies any declared range (`^1.0.0`, `>=1.0.0,<2.0.0`, etc.).
- A bare cross-reference with no `@version` resolves to the highest installed version.

## 3. Device template

Defines a device family: how to recognize it (`signature`), its hardware variants, which
characteristics carry which data (`channels`), and which other templates it pulls in
(`references`).

```json
{
  "schema_version": 1,
  "id": "builtin.example-device",
  "version": "1.0.0",
  "type": "device",
  "name": "Example Device",
  "signature": {
    "service_uuids": ["0000abcd-0000-1000-8000-00805f9b34fb"],
    "name_prefix": "EX"
  },
  "variants": [
    { "variant_id": "v1", "name": "Model One", "signature": { "name_prefix": "EX1" } }
  ],
  "channels": [
    { "name": "data", "service_uuid": "0000abcd-...", "char_uuid": "0000abce-...", "operation": "notify" }
  ],
  "references": { "display": "builtin.example-display@^1.0.0" }
}
```

**Signature matching:** discovered GATT service UUIDs must contain *all* `service_uuids` listed.
`name_prefix` and `manufacturer_data`, if present, must also match. Unspecified fields are
wildcards. The most specific matching variant wins.

> **UUID caution:** use the device's *actual* advertised UUIDs. Many devices use vendor-specific
> 128-bit UUIDs (e.g. `961f0001-d2d6-43e3-a417-3bb8217e0e01`), **not** the Bluetooth-base
> `...-0000-1000-8000-00805f9b34fb` form. Signature and characteristic matching fail if the
> wrong form is used.

## 4. Display template

Defines how to parse and render a characteristic's bytes. Structure:

```json
{
  "schema_version": 1,
  "id": "builtin.example-display",
  "version": "1.0.0",
  "type": "display",
  "default_view": "metric",
  "notifications": [
    {
      "char": "0000abce-0000-1000-8000-00805f9b34fb",
      "description": "...",
      "views": {
        "raw":    { "fields": [ ... ] },
        "metric": { "fields": [ ... ] }
      }
    }
  ],
  "reads": []
}
```

- `notifications[]` — entries for notify/indicate characteristics.
- `reads[]` — entries for read characteristics (same shape).
- `views` — named field sets (`raw`, `metric`, `imperial`, or any string you choose). The user
  switches views in the agent UI. `default_view` sets the initial one.
- Each view has a `fields[]` array. Fields with `"display": false` are parsed and usable as inputs
  to `expr`/`formula` fields but not shown in the UI.

## 5. Field types

Every field declares a `type`. If the agent encounters an unknown `type`, it shows the raw hex
for that field plus a warning (forward-compatible).

| Type | Purpose | Key fields |
|---|---|---|
| `raw` | Hex display, no interpretation | `offset`, `length`, `encoding` |
| `scale_offset` | Linear transform: `value = raw * scale + offset_value` | `scale`, `offset_value`, `unit`, `precision` |
| `bitmask` | Interpret individual bits as flags | `bits[]` with `bit`, `label`, `values` |
| `enum` | Map a byte value to a label | `values` map |
| `expr` | Compute from sibling fields by `id` | `expr` string (+, -, \*, /, parens) |
| `formula` | Named built-in function | `formula`, `inputs` map |

Built-in formulas (v1): `density_altitude`.

`expr` example (°F from a hidden °C field):
```json
{ "id": "temp_c", "type": "scale_offset", "offset": 8, "length": 2, "encoding": "int16_le",
  "scale": 0.1, "offset_value": 0.0, "display": false },
{ "id": "temp_f", "type": "expr", "expr": "temp_c * 9 / 5 + 32", "unit": "°F", "precision": 1, "display": true }
```

## 6. Encodings

| Value | Description |
|---|---|
| `uint8` / `int8` | 8-bit unsigned / signed |
| `uint16_be` / `uint16_le` | 16-bit unsigned, big / little endian |
| `int16_be` / `int16_le` | 16-bit signed, big / little endian |
| `uint32_be` / `uint32_le` | 32-bit unsigned |
| `int32_be` / `int32_le` | 32-bit signed |
| `float32_be` / `float32_le` | IEEE 754 single precision |
| `bytes` | Raw byte array (hex display only) |
| `utf8` | UTF-8 string |

## 7. Codec template

Defines framing applied before field parsing (e.g. a UART-over-BLE wrapper). Referenced by a
device template's `references.codec`. See `catalog/builtin/shared/codec.niimbot-uart-framed.json`
for a worked example. Built-in codec types: `raw` (no framing), `wrapped` (header/length/data/
checksum/tail).

## 8. Component template

A reusable partial for standard GATT services, shared across device families. Same `notifications`
/`reads` shape as a display template, with `"type": "component"`. A display template includes
components via a top-level `includes` array; the broker merges component fields in at load time.
See the Battery Service and Device Information components under `catalog/builtin/shared/`.

## 9. Notification matching

When one characteristic carries multiple response types, add a `match` block to select the field
layout by a command byte:

```json
{
  "char": "...",
  "match": { "cmd_byte_offset": 2, "cmd_byte_value": "0xDB" },
  "views": { ... }
}
```

Entries for the same characteristic are evaluated in order; the first match wins. An entry with no
`match` block is the catch-all fallback.
