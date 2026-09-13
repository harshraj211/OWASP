# A07 Hard: Password Reset Token Prediction (Apex BioLogistics)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Hard (Cryptographic PRNG State Recovery)
* **Default Port:** 6021
* **Concept:** PRNG State Recovery, Linear Congruential Generator Prediction, Account Takeover

---

### Challenge Description
Apex BioLogistics manages global cold-chain distribution for Phase III immunotherapy clinical trials. To streamline investigator operations, the platform provides self-service password recovery.

However, the recovery token generator relies on an insecure linear congruential pseudo-random number generator (LCG). An attacker can observe sequential tokens generated for low-privilege accounts in the research relay outbox, recover the internal PRNG state, predict the next token issued for the administrative review account, and seize full control of the platform.

### Objective
1. Explore the platform and registered clinical trial protocols to enumerate investigator and oversight review accounts.
2. Analyze the password recovery workflow and token issuance behavior via the research relay outbox.
3. Recover the internal pseudo-random state of the token generator to predict the administrative recovery token.
4. Reset the Chief Medical Director password, authenticate, and access the restricted Clinical Governance Vault at `/admin/governance` to recover the dynamic flag.
