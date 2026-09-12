# A07 Easy: Weak Password Policy (AeroFleet Operations)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Easy (Hard-calibrated enterprise scenario)
* **Default Port:** 6019
* **Concept:** Multi-Page Enumeration, Targeted Password Spraying & Legacy Password Policy Bypass

---

### Challenge Description
AeroFleet Global manages commercial air transport and international VIP charter logistics. During a phased migration to an enterprise SSO solution, older dispatch workstation accounts were grandfathered under a predictable default credential schema.

The authentication portal enforces strict consecutive failure lockouts (5 failed attempts locks an account). Attackers must explore the platform, enumerate operational bulletins and personnel rosters, deduce the grandfathered credential structure, and compromise the Chief Dispatcher account to view restricted diplomatic flight manifests.

### Objective
Enumerate the crew directory and IT security bulletins, deduce the default legacy password for Chief Dispatcher Marcus Vance (`m.vance`), authenticate, and access the restricted diplomatic cargo manifest at `/dispatch/manifest/classified` to recover the dynamic flag.
