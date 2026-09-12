# A04 Medium: Cryptographic Hash Length Extension & Signature Forgery

### Category: OWASP Top 10:2025 - A04 Cryptographic Failures
* **Difficulty:** Medium
* **Default Port:** 6011
* **Concept:** Hash Length Extension Attack on Merkle-Damgard Hash Functions (SHA-256)

---

### Challenge Description
The RedTeam Hacker Academy Document Retrieval Gateway secures file download requests using a custom Message Authentication Code (MAC) scheme designed as:
`MAC = SHA256(SECRET || filename)`

Because the application concatenates secret data directly before the payload rather than utilizing an authenticated HMAC construction (such as RFC 2104 HMAC), it is vulnerable to a classic **Hash Length Extension** attack. Knowing the length of the secret (16 bytes) and the valid MAC for `public_report.pdf`, an attacker can reconstruct the internal SHA-256 state and forge a valid MAC for an extended payload containing null bytes and `flag.txt`.

### Objective
Calculate the Merkle-Damgard padding for the original data and secret, extend the hash state to include `../../../../flag.txt`, and submit the forged URL to download the dynamic flag.
