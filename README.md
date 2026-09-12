# RedTeam Hacker Academy — OWASP Top 10 (2025) CTF & Training Labs

Comprehensive, Dockerized CTF training environment for the **OWASP Top 10 (2025) Web Security Standard**. Features an interactive centralized training portal, dynamic flags, automated challenge lifecycle orchestration, and authentic multi-page enterprise web applications.

---

## Architecture Overview

```
Client Browser
      │
      ▼
OWASP Training Portal (Flask Dashboard :8000)
      │
      ▼ (API: /api/launch-lab, /api/submit-flag)
Orchestration Script (scripts/start_challenge.sh)
      │
      ├── Generates dynamic instance flag: RTSA{<challenge_key>_<token>}
      ├── Manages single-active container lifecycle
      └── Port-forwards to isolated challenge container
            │
            ▼
Active Vulnerable Lab Instance (Ports: 6001–6030)
```

---

## Challenge Catalog & Ports

### A01:2025 – Broken Access Control
- **Easy (Port 6001)**: `a01-easy` — Horizontal Privilege Escalation (IDOR)
- **Medium (Port 6002)**: `a01-medium` — MeridianHR Vertical Privilege Escalation
- **Hard (Port 6003)**: `a01-hard` — Asterion Benefits Exchange (CORS Misconfiguration)

### A02:2025 – Security Misconfiguration
- **Easy (Port 6004)**: `a02-easy` — Exposed Sensitive Files (.git, .env.backup)
- **Medium (Port 6005)**: `a02-medium` — Nginx Off-by-Slash & Reverse Proxy Traversal
- **Hard (Port 6006)**: `a02-hard` — Web Cache Deception & Request Smuggling

### A03:2025 – Software Supply Chain Failures
- **Easy (Port 6007)**: `a03-easy` — Known Component CVE Exploitation
- **Medium (Port 6008)**: `a03-medium` — Dependency Confusion & Poisoned Package
- **Hard (Port 6009)**: `a03-hard` — Log4Shell / JNDI Supply Chain Attack

### A04:2025 – Cryptographic Failures
- **Easy (Port 6010)**: `a04-easy` — JWT Key Traversal & Signature Bypass
- **Medium (Port 6011)**: `a04-medium` — Cryptographic Hash Length Extension
- **Hard (Port 6012)**: `a04-hard` — AES-256-CBC Padding Oracle Attack

### A05:2025 – Injection
- **Easy (Port 6013)**: `a05-easy` — SQLite Authentication Bypass (WAF Evasion)
- **Medium (Port 6014)**: `a05-medium` — Server-Side Request Forgery (SSRF)
- **Hard (Port 6015)**: `a05-hard` — Blind Server-Side Template Injection (SSTI)

### A07:2025 – Authentication Failures
- **Easy (Port 6019)**: `a07-easy` — AeroFleet Global: Weak Password Policy & Targeted Password Spray
- **Medium (Port 6020)**: `a07-medium` — Aegis Global Treasury: MFA State Machine Bypass & SecOps Headers
- **Hard (Port 6021)**: `a07-hard` — Apex BioLogistics: LCG Password Reset PRNG Token Prediction

### A08:2025 – Software or Data Integrity Failures
- **Easy (Port 6022)**: `a08-easy` — Novus CMS: Unsigned Plugin Installation & Code Execution
- **Medium (Port 6023)**: `a08-medium` — VortexEdge SCADA: Insecure Update Mechanism & Firmware Tampering
- **Hard (Port 6024)**: `a08-hard` — AeroData Analytics: Unsafe Deserialization & Python Pickle Sandbox Escape

### A09:2025 – Security Logging and Alerting Failures
- **Easy (Port 6025)**: `a09-easy` — Sentinel SOC: Missing Login Logs & Unlogged Partner SSO Endpoint
- **Medium (Port 6026)**: `a09-medium` — Apex Global Bank: CRLF Log Injection & Compliance Monitor Deception
- **Hard (Port 6027)**: `a09-hard` — Titan Defense: Audit Log Tampering & Cryptographic Hash-Chain Reconstruction

### A10:2025 – Mishandling of Exceptional Conditions
- **Easy (Port 6028)**: `a10-easy` — QuantEdge Capital: Information Disclosure Through Unhandled Exceptions
- **Medium (Port 6029)**: `a10-medium` — Synapse SCADA Grid: Telemetry Exception Denial of Service / Fail-Open
- **Hard (Port 6030)**: `a10-hard` — OmniPress Media: File Upload Validation Bypass via Exception Mishandling to RCE

---

## Quick Start

### 1. Launch Central Portal
```bash
python3 app.py
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
* **Default Username:** `redteamacademy`
* **Default Password:** `redteamacademy`

### 2. Launch Specific Challenge Directly via CLI
```bash
# Category A07
bash scripts/start_challenge.sh A07 easy     # Port 6019
bash scripts/start_challenge.sh A07 medium   # Port 6020
bash scripts/start_challenge.sh A07 hard     # Port 6021

# Category A08
bash scripts/start_challenge.sh A08 easy     # Port 6022
bash scripts/start_challenge.sh A08 medium   # Port 6023
bash scripts/start_challenge.sh A08 hard     # Port 6024

# Category A09
bash scripts/start_challenge.sh A09 easy     # Port 6025
bash scripts/start_challenge.sh A09 medium   # Port 6026
bash scripts/start_challenge.sh A09 hard     # Port 6027

# Category A10
bash scripts/start_challenge.sh A10 easy     # Port 6028
bash scripts/start_challenge.sh A10 medium   # Port 6029
bash scripts/start_challenge.sh A10 hard     # Port 6030
```

### 3. Dynamic Flag Validation
Submit the recovered flag through the portal UI or the API:
```bash
curl -X POST http://127.0.0.1:8000/api/submit-flag \
  -H "Content-Type: application/json" \
  -d '{"flag": "RTSA{...}"}'
```
