# A09 Easy: Missing Login Logs (Sentinel SOC)

### Category: OWASP Top 10:2025 - A09 Security Logging and Alerting Failures
* **Difficulty:** Easy (Hard-Calibrated Multi-Page Target)
* **Default Port:** 6025
* **Concept:** Unlogged Authentication Endpoint, SIEM Sensor Evasion, Brute Force Detection Failure

---

### Challenge Description
Sentinel SOC operates a centralized Security Information and Event Management (SIEM) gateway that logs authentication events on `/login`. When an IP generates 3 failed login attempts, the automated sensor immediately blacklists the source IP address.

However, an unlogged legacy partner single sign-on endpoint (`/api/v1/sso/partner-auth`), documented in `/api/v1/docs`, completely omits logging failed attempts and fails to trigger SIEM alarms.

### Objective
1. Inspect `/compliance` to identify the Lead Compliance Auditor profile (`sec_auditor` / `Auditor2026!`) and inspect `/api/v1/docs` for exposed authentication routes.
2. Authenticate through the unlogged endpoint `/api/v1/sso/partner-auth` without triggering SIEM detection.
3. Access `/auditor/vault` to retrieve the dynamic compliance audit flag.
