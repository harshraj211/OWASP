# A07 Medium: Multi-Factor Authentication (MFA) Bypass (Aegis Global Treasury)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Medium (Enterprise State Machine Bypass)
* **Default Port:** 6020
* **Concept:** Multi-Stage Authentication State Machine Bypass & SecOps Disaster Recovery Elevation

---

### Challenge Description
Aegis Global Treasury manages bilateral high-value gross settlements for international investment banks. Administrative sessions demand multi-factor authentication (hardware TOTP 6-digit codes) before clearance into the Executive Vault is granted.

During ongoing infrastructure failover operations, undocumented emergency session elevation pathways were integrated into the authentication pipeline to ensure business continuity for automated settlement routines.

### Objective
1. Explore the institutional settlement platform and operational advisories to discover temporary administrative maintenance credentials and active disaster recovery incident parameters.
2. Authenticate as the root administrative operator and analyze the multi-factor authentication state controller.
3. Leverage the SecOps emergency dispatch elevation protocol to bypass the secondary verification requirement and access `/security/audit-vault` to extract the dynamic flag.
