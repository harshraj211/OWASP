# A08 Easy: Unsigned Plugin Installation (Novus CMS)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Easy (Hard-Calibrated Multi-Page Target)
* **Default Port:** 6022
* **Concept:** Unverified Extension Bundles, Developer Bypass Flags, Server-Side Code Execution

---

### Challenge Description
Novus Enterprise CMS delivers content for international media portals. The platform allows editorial staff to extend capabilities by uploading `.zip` plugin packages. 

While the system ostensibly mandates that all plugins carry digital signatures certified by Novus CA, an insecure fallback allows bypass during testing when configured with `verification_mode: "developer_bypass"` and `environment: "sandbox"`. Once installed, plugin tasks are executed directly within the host runtime.

### Objective
1. Inspect public documentation and staff memos at `/articles` to discover the editorial lead account (`editor`) and password protocol (`NovusEditorial2026!`).
2. Authenticate to the editorial suite at `/login`.
4. Package a malicious ZIP extension containing `plugin.py` and a `manifest.json` configured with developer bypass parameters.
5. Upload the archive at `/admin/plugins/upload`, trigger `/admin/plugins/run/<id>`, and capture the dynamic flag from `/flag.txt`.
