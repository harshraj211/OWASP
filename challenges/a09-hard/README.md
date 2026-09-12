# A09 Hard: Audit Log Tampering (Titan Defense Strategic Systems)

### Category: OWASP Top 10:2025 - A09 Security Logging and Alerting Failures
* **Difficulty:** Hard (Insanely Hard Level)
* **Default Port:** 6027
* **Concept:** Cryptographic Audit Hash-Chain Manipulation, Evidence Redaction, Sentinel Integrity Verification

---

### Challenge Description
Titan Defense Strategic Systems protects classified Special Access Programs (SAP) using a tamper-evident cryptographic audit ledger. Any attempt to access `/vault/classified` without prior authorization triggers an alarm and appends an `UNAUTHORIZED_BREACH_DETECTED` block to the blockchain-like audit trail.

The vault's automated Sentinel interlock permanently seals the vault as long as any breach event is recorded in the ledger OR if the SHA-256 hash chain is broken.

### Objective
1. Visit `/vault/classified` to trigger the intrusion alert and inspect the resulting block in `/audit/ledger`.
2. Inspect client assets (`/static/js/titan_audit.js`) to discover the SecOps maintenance key (`TITAN_SEC_MAINT_2026`).
3. Access `/audit/console` or the REST API to tamper with the breach block, modifying its event type to `ROUTINE_SECURITY_PATROL`.
4. Recompute the cryptographic hash chain using `/api/v1/audit/recompute-chain` to satisfy Sentinel integrity verification.
5. Revisit `/vault/classified` to extract the dynamic classified flag.
