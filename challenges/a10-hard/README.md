# A10 Hard: File Upload Validation Bypass via Exception Mishandling (OmniPress Media)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Hard (Insanely Hard Level)
* **Default Port:** 6030
* **Concept:** Image Header Exception Trigger, Multi-Stage Pipeline Fail-Open, Web Shell Upload to RCE

---

### Challenge Description
OmniPress Media Suite operates an automated asset ingestion pipeline that validates uploaded images and editorial graphics. The validation process runs in two sequential stages:
1. **Stage 1 (Header Verification)**: Validates image container structures (PNG, JPEG, GIF).
2. **Stage 2 (Malware Detection)**: Scans file content for prohibited shell commands (`import os`, `subprocess`, `system`, `eval`).

However, if an `ImageHeaderError` occurs during Stage 1 (such as uploading a malformed PNG lacking the required IHDR chunk marker or a `CORRUPT_RAW_STREAM` header), an unhandled exception fallback activates. The fallback assumes the file is an unformatted raw asset, completely bypasses the Stage 2 malware scan, and writes the file into `static/scripts/` using its original filename.

Staged scripts can then be executed via the Editorial Script Terminal at `/editorial/terminal`.

### Objective
1. Inspect the upload pipeline specifications in `/articles`.
2. Craft a Python script (e.g. `exploit.py`) prepended with an exception trigger (such as `CORRUPT_RAW_STREAM\n#` or malformed PNG bytes) containing code to read the dynamic flag.
3. Upload `exploit.py` at `/media/upload` to trigger the `ImageHeaderError` fail-open fallback, staging it into `static/scripts/`.
4. Execute `exploit.py` via `/editorial/run-automation` at `/editorial/terminal` to capture the dynamic flag.
