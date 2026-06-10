# Security Policy

## Supported versions

BT Bridge is pre-1.0 (`0.x`). Security fixes to the catalog tooling are applied to the latest
released `0.x` version only.

| Version | Supported |
|---|---|
| latest `0.9.x` | ✅ |
| older `0.x` | ❌ |

## Reporting a vulnerability

**Please do not open a public issue for security vulnerabilities.**

Report privately through either channel:

1. **GitHub private vulnerability reporting** (preferred) — on this repository, go to the
   **Security** tab → **Report a vulnerability**.
2. **Email** — `security@coldboreballisticsllc.com` with a description, affected commit, and
   reproduction steps.

## What to expect

- **Acknowledgement** within 5 business days.
- An assessment and remediation plan if confirmed.
- Coordinated disclosure with credit unless you prefer anonymity.

## Scope notes

This repository is a **data catalog** plus its lint/index tooling. The templates are JSON data, not
executable code — but they are consumed by the broker and agent, so in-scope concerns include:
a malicious or malformed template/index that could cause a consumer to crash, traverse paths, or
bypass the catalog's `sha256` integrity check; and vulnerabilities in the `tools/` lint/index
scripts. A reported issue affecting how a *consumer* handles catalog content may be routed to the
broker or agent repository as appropriate.

---

*Part of the BT Bridge project by Cold Bore Ballistics, LLC.*
