# A08 Easy: Unsigned Plugin Installation (Novus CMS)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Easy (Hard-Calibrated Multi-Page Target)
* **Default Port:** 6022
* **Concept:** Unverified Extension Bundles, Developer Bypass Flags, Server-Side Code Execution

---

### Challenge Description
Novus Enterprise CMS delivers content for international media portals. The platform allows editorial staff to extend capabilities by uploading `.zip` plugin packages. 

While the system ostensibly mandates that all plugins carry digital signatures certified by Novus CA, an insecure fallback allows bypass using `"verification_mode": "developer_bypass"` or `"signature_algorithm": "none"`. Once installed, plugin tasks are executed directly within the host runtime.

### Objective
Log into the editorial console (`editor` / `EditorNovus2026!`), package a malicious ZIP extension with a bypassing `manifest.json` and a payload script `plugin.py`, upload the archive at `/admin/plugins/upload`, trigger `/admin/plugins/run/<id>`, and capture the dynamic flag from `/flag.txt`.
