# A07 Medium: Multi-Factor Authentication (MFA) Bypass

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Medium (Very Difficult Level)
* **Default Port:** 6020
* **Concept:** Multi-Stage Authentication State Machine Bypass & Leaked SecOps Internal Headers

---

### Challenge Description
Aegis Clearinghouse manages bilateral high-value gross settlements for international investment banks. Administrative sessions demand multi-factor authentication (TOTP 6-digit codes) protected by rate limits.

However, automated test suites and disaster-recovery protocols introduced undocumented session elevation pathways into the authentication flow.

### Objective
1. Enumerate `/services` and JavaScript client assets to discover leaked credentials (`sysadmin_root` / `AutumnSettlement#99`) and internal SecOps headers (`X-SecOps-Internal: 1` or `/api/v1/auth/session/upgrade`).
2. Log in as `sysadmin_root` and bypass the 2FA enforcement stage.
3. Access `/security/audit-vault` to extract the dynamic flag.
