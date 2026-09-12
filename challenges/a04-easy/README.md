# A04 Easy: JWT Key Traversal & Signature Forgery

### Category: OWASP Top 10:2025 - A04 Cryptographic Failures
* **Difficulty:** Easy
* **Default Port:** 6010
* **Concept:** Insecure JWT Key ID (`kid`) Header Resolution / Path Traversal

---

### Challenge Description
The RedTeam Hacker Academy Enterprise Key Governance Portal validates incoming session tokens using JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`).
During token verification, the backend inspects the token's unverified header for a `kid` (Key ID) parameter and resolves the signing secret file from the filesystem.

Because the `kid` parameter is not properly sanitized or restricted to an allowlist, an attacker can supply directory traversal sequences (`../`) to force the server into reading predictable or empty files on the underlying filesystem (such as `/dev/null` or `/proc/sys/kernel/domainname`) to verify the HMAC signature.

### Objective
Forge a valid administrative session token (`role: admin`) using a predictable signing secret via `kid` path traversal, authenticate to the portal, and unlock the master cryptographic vault to retrieve the dynamic flag.
