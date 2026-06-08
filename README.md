# BT Bridge Templates

A community catalog of **device, display, codec, and component templates** for the
[BT Bridge](https://github.com/ColdBoreBallistics/bt-bridge-broker) Bluetooth Low Energy
hardware-test harness.

BT Bridge agents render live BLE notification and read data using *display templates*, and
identify connected devices using *device templates* and their *signatures*. This repository is
the canonical, versioned catalog those templates are published to and pulled from. The BT Bridge
broker ships a small set of built-in templates so it works out of the box; everything else lives
here, and users install the templates they want — by name, on demand.

> **Templates are data, not code.** A template is a JSON file describing how to decode a device's
> BLE payloads. Contributing a template requires no programming — just the device's GATT layout
> and the byte meanings. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## What's in here

| Path | Contents |
|---|---|
| `catalog/builtin/` | First-party templates maintained by the BT Bridge project (`builtin.*` IDs). |
| `catalog/community/` | Community-contributed templates (`contrib.*` IDs). |
| `catalog/index.json` | Machine-readable catalog index — generated, the source of truth for clients. |
| `schema/` | JSON Schemas for each template type (validated in CI). |
| `tools/` | Index builder and lint utilities. |
| `docs/` | Template authoring guide, field-type reference, governance. |

## How clients consume the catalog

The BT Bridge broker fetches `catalog/index.json` **on demand** (it is not vendored into the
broker), shows the user the available templates, and downloads only the ones they select into the
broker's active `templates/` directory. There are two front ends, because choice matters:

- **CLI** — `python3 tools/fetch_templates.py` in the broker repo: list, search, and install
  templates non-interactively (CI-friendly).
- **Web** — the broker's `/v1/templates/catalog` endpoint and selection page: browse and install
  interactively.

Both read the same `catalog/index.json` and write into the same `templates/` directory.

## Template types

| Type | Purpose |
|---|---|
| `device` | Device family: signature (how to recognize it), variants, channel wiring, cross-references. |
| `display` | How to parse and render a characteristic's bytes into labeled fields and views. |
| `codec` | Framing/deframing layer applied before field parsing (e.g. Niimbot UART framing). |
| `component` | Reusable partial for standard GATT services (Battery, Device Information). |

The authoritative format specification lives in
[`docs/TEMPLATE_FORMAT.md`](docs/TEMPLATE_FORMAT.md).

## Versioning

Each template carries its own semantic version (`"version": "1.2.0"`). The catalog can hold
multiple versions of the same template ID simultaneously; clients resolve the highest version
satisfying any declared range. The repository itself is **not** tagged in lockstep with the BT
Bridge app — template versions are independent.

## License

Templates and code in this repository are licensed under [Apache-2.0](LICENSE).

---

*Part of the BT Bridge hardware-test tooling by Cold Bore Ballistics, LLC.*
