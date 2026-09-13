# A10 Hard: Image Polyglot File Upload Validation Bypass via Exception Mishandling (OmniPress Media)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Hard (10/10 Calibrated)
* **Default Port:** 6030
* **Concept:** Image Container Parsing Exception, Multi-Stage Pipeline Fail-Open, Polyglot Web Shell Upload to RCE

---

### Challenge Description
OmniPress Media Suite operates an automated asset ingestion pipeline that validates uploaded images and editorial graphics. The validation process runs in two sequential stages:
1. **Stage 1 (Container Header Verification)**: Validates image container formats (PNG, JPEG, GIF).
2. **Stage 2 (Malware Signature Inspection)**: Scans file content for prohibited execution signatures (`import os`, `subprocess`, `system`, `eval`, `popen`, etc.).

### The Vulnerability (Mishandling of Exceptional Conditions)
When an asset fails Stage 1 with an `ImageHeaderError` (such as a GIF container missing the required Image Descriptor chunk `0x2C` or a corrupted PNG structure), the upload controller catches the exception and initiates an insecure fallback path. 

The fallback logic assumes the asset is an unformatted legacy binary, completely **skips Stage 2 malware scanning**, and stores the file using its raw filename into the internal scripts workspace (`static/scripts/`).

Staged scripts can subsequently be executed via the Editorial Script Terminal (`/editorial/terminal`).

### Polyglot Crafting
Because the file will be executed by the Python interpreter, the uploaded file must be syntactically valid Python code while simultaneously starting with an image magic byte signature recognized by Stage 1:
```python
GIF89a = 1
import os
print("FLAG:" + os.environ.get("FLAG", ""))
```
* **Stage 1 Evaluation:** The file starts with `GIF89a`. The container validator detects that the stream lacks the binary Image Descriptor block `0x2C` and raises `ImageHeaderError`.
* **Exception Fallback:** The server catches `ImageHeaderError`, bypasses the Stage 2 malware scan, and archives the file into `static/scripts/`.
* **Python Execution:** The file begins with `GIF89a = 1` (a valid integer assignment), followed by Python code to extract `/flag.txt` or `$FLAG`.

### Objective
1. Identify the media validation stages and the Editorial Script Terminal.
2. Craft a GIF/Python polyglot script that triggers `ImageHeaderError` to bypass the malware scanner.
3. Upload the script via `/media/upload`.
4. Trigger script execution via `/editorial/run-automation` at `/editorial/terminal` to capture the dynamic flag.
