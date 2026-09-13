# A07 Easy: Weak Password Policy & Rate-Limit Bypass (AeroFleet Operations)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Easy (Enterprise Rate-Limit Evasion & Targeted Spray)
* **Default Port:** 6019
* **Concept:** Username Enumeration, Reverse-Proxy Header Spoofing (`X-Forwarded-For`), Targeted Password Spraying

---

### Challenge Description
AeroFleet Global manages commercial air transport and international charter logistics. The operations dispatch portal protects crew accounts with IP-based rate limiting (blocking addresses after 3 failed attempts).

However, flawed client IP extraction trusts unvalidated reverse-proxy headers, and the authentication handler returns distinct responses for registered vs. unregistered identifiers. Security analysts must enumerate the personnel directory, confirm the authorized Chief Dispatcher account, evade rate-limiting via header spoofing, and spray candidate operational credentials to access the restricted diplomatic cargo manifest.

### Objective
1. Enumerate the crew directory and IT security bulletins to identify the Chief Flight Dispatcher account.
2. Evade the portal's IP-based rate limiting using spoofed proxy headers (`X-Forwarded-For`).
3. Spray common operational credentials to compromise the dispatcher account, and access `/dispatch/manifest/classified` to recover the dynamic flag.
