# A07 Medium: Multi-Factor Authentication (MFA) Bypass (Aegis Global Treasury)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Medium (Authentication State Machine & Type Juggling Bypass)
* **Default Port:** 6020
* **Concept:** Multi-Stage Authentication Workflow, API Flaws, Null-Value Type Equivalence in 2FA Recovery

---

### Challenge Description
Aegis Global Treasury manages bilateral high-value gross settlements for international investment banks. Access to the Executive Vault demands primary institutional credentials followed by mandatory hardware TOTP multi-factor authentication.

To support disaster recovery scenarios where operators lose access to physical authenticators, the platform provides an emergency backup verification API (`/api/v1/auth/verify-backup`). However, the recovery verification logic contains an authentication flaw in how uninitialized database fields and JSON payload types are evaluated.

### Objective
1. Inspect the institutional settlement portal to identify primary administrative operator credentials.
2. Authenticate through primary login and proceed to the secondary multi-factor verification stage.
3. Analyze the emergency backup code verification mechanism to identify and exploit the null-equivalence flaw, elevate the administrative session, and access `/security/audit-vault` to extract the dynamic flag.
