# A09 Medium: Log Injection (Apex Global Commercial Bank)

### Category: OWASP Top 10:2025 - A09 Security Logging and Alerting Failures
* **Difficulty:** Medium (Very Difficult Level)
* **Default Port:** 6026
* **Concept:** CRLF Log Injection, Audit Trail Spoofing, Automated Compliance Daemon Deception

---

### Challenge Description
Apex Global Commercial Bank operates an automated compliance daemon that monitors the live transaction audit stream (`audit.log`). When the daemon detects a valid regulatory audit override entry, it unlocks high-value transfers in the Treasury Vault.

However, the wire transfer submission form concatenates the user-supplied remittance advice memo directly into `audit.log` without sanitizing newline characters (`\r\n` / `\n`). An attacker can inject a spoofed `[AUDIT_OVERRIDE]` record with the active daily clearance token to fool the compliance monitor.

### Objective
1. Inspect `/compliance/status` to determine today's active compliance verification token and regex format.
2. Submit a wire transfer at `/transfer` with a newline-injected payload in the `memo` field mimicking a certified audit override.
3. Verify that the compliance monitor in `/compliance/status` accepts the override.
4. Navigate to `/vault/treasury` to unlock and claim the dynamic flag.
