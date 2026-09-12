# A07 Hard: Password Reset Token Prediction (Apex BioLogistics)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Hard (Insanely Hard Level)
* **Default Port:** 6021
* **Concept:** PRNG State Recovery, Linear Congruential Generator (LCG) Prediction, Account Takeover

---

### Challenge Description
Apex BioLogistics manages global cold-chain distribution for Phase III immunotherapy clinical trials. To streamline investigator operations, the platform provides self-service password recovery.

However, the recovery token generator relies on an insecure linear congruential pseudo-random number generator (LCG). An attacker can observe sequential tokens generated for low-privilege accounts in the research relay outbox, recover the internal PRNG state, predict the next token issued for the administrative review account, and seize full control of the platform.

### Objective
1. Enumerate the trial registry to discover the Chief Medical Director account (`admin@apexbiologistics.net`) and the researcher account (`researcher_demo@apexbiologistics.net`).
2. Request a password reset for `researcher_demo@apexbiologistics.net` and inspect the issued token $T_1$ in `/outbox`.
3. Immediately request a password reset for `admin@apexbiologistics.net`.
4. Predict the administrator token $T_{admin} = (A \cdot T_1 + C) \pmod M$ using Numerical Recipes LCG parameters ($A = 1664525, C = 1013904223, M = 2^{32}$).
5. Reset the administrator password at `/reset-password`, log in, and access `/admin/governance` to recover the dynamic flag.
