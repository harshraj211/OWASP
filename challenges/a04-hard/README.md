# A04 Hard: AES-256-CBC Padding Oracle Attack

### Category: OWASP Top 10:2025 - A04 Cryptographic Failures
* **Difficulty:** Hard
* **Default Port:** 6012
* **Concept:** PKCS#7 Padding Oracle Side-Channel Decryption & CBC Ciphertext Forgery

---

### Challenge Description
The RedTeam Hacker Academy Encrypted Session Terminal authorizes user requests through an AES-256-CBC encrypted session cookie formatted as `base64(IV + Ciphertext)`.
Upon receiving a request, the server decrypts the cookie and validates the PKCS#7 padding:
- If padding verification fails, it emits an unhandled `500` error with message `Decryption Error: Invalid padding bytes.`
- If padding is valid but the decrypted string is not valid JSON, it returns `200` with `Session Error: Invalid JSON structure.`
- If padding and JSON are both valid, it executes the session logic and checks if `role == "admin"`.

This differentiated error feedback provides an infallible padding oracle side-channel.

### Objective
Leverage the padding oracle side-channel to decrypt the session blocks, forge an encrypted payload representing `{"role": "admin", "id": 999}`, and submit the forged cookie to claim the administrative flag.
