# A07 Easy: Weak Password Policy (AeroFleet Operations)

### Category: OWASP Top 10:2025 - A07 Authentication Failures
* **Difficulty:** Easy (Enterprise Multi-Page Enumeration)
* **Default Port:** 6019
* **Concept:** Multi-Page Enumeration, Targeted Password Deduction & Legacy Provisioning Schema

---

### Challenge Description
AeroFleet Global manages commercial air transport and international charter logistics. During a phased migration to an enterprise SSO solution, older dispatch workstation accounts were grandfathered under a default corporate credential schema.

The authentication portal enforces strict consecutive failure lockouts (5 failed attempts locks an account). Security analysts must explore the platform, enumerate operational bulletins and personnel rosters, identify which role holds diplomatic clearance, deduce the legacy credential format, and authenticate to inspect the restricted diplomatic flight manifest.

### Objective
Enumerate the crew directory and IT security bulletins, deduce the default legacy dispatch credentials for the authorized operations role, authenticate, and access the restricted diplomatic cargo manifest at `/dispatch/manifest/classified` to recover the dynamic flag.
