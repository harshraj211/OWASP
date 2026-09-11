"""A02 Hard: Security Misconfiguration - Enterprise API Gateway Desync & Service Mesh Signing Forgery.

OWASP Top 10:2025 A02 - Security Misconfiguration

Vulnerability Chain:
1. Reverse Proxy Gateway ACL Mismatch:
   The gateway restricts external access to `/api/v1/internal/*` using a strict prefix check.
   Due to WSGI path normalization desync (matrix parameters `;`, encoded slashes `..%2f`, or encoded dots `%2e%2e`),
   an attacker can bypass the gateway ACL by requesting:
   `GET /api/v1/cluster/%2e%2e/internal/env` or `GET /api/v1;param/internal/env`
2. Actuator / Production Environment Exposure:
   The internal management endpoint `/api/v1/internal/env` is mistakenly exposed in production,
   leaking the internal microservice mesh topology, the air-gapped vault endpoint, and the shared HMAC signing secret.
3. Service Mesh Cryptographic Request Forgery:
   The air-gapped vault `/api/v1/internal/vault/keys` validates incoming requests using an HMAC-SHA256 signature header:
   `X-Cluster-Gateway-Signature: HMAC-SHA256(secret, "{timestamp}.GET./api/v1/internal/vault/keys")`
   and requires `X-Cluster-Identity: cluster_super_admin`.
   By computing the HMAC signature using the leaked secret, the attacker unlocks the master vault key and captures the flag.
"""

import hashlib
import hmac
import os
import posixpath
import re
import secrets
import time
import urllib.parse
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

def instance_flag() -> str:
    configured = os.environ.get("FLAG", "").strip()
    if configured:
        return configured
    return f"RTSA{{a02_hard_gateway_mesh_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = instance_flag()
INTERNAL_MESH_SECRET = "rta_mesh_vault_sec_89d3c2b1a0f4e6"

# WSGI RFC Path Normalization Middleware
class PathNormalizationMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        raw_path = environ.get("PATH_INFO", "")
        # Preserve original unnormalized path for Gateway ACL inspection
        environ["RAW_REQUEST_PATH"] = raw_path

        # Backend application framework path normalizer:
        # Decodes URL escapes, strips matrix parameters, and normalizes path traversal
        unquoted = urllib.parse.unquote(raw_path)
        stripped_params = re.sub(r";[^/]*", "", unquoted)
        collapsed = re.sub(r"/+", "/", stripped_params)
        environ["PATH_INFO"] = posixpath.normpath(collapsed)

        return self.wsgi_app(environ, start_response)

app.wsgi_app = PathNormalizationMiddleware(app.wsgi_app)

# Gateway ACL Filter
@app.before_request
def gateway_access_control():
    raw_path = request.environ.get("RAW_REQUEST_PATH", request.path)

    # Gateway policy strictly blocks external calls to internal management routes
    if re.match(r"^/api/v1/(internal|vault|actuator)(/.*)?$", raw_path):
        return jsonify({
            "status": "error",
            "code": 403,
            "error": "Gateway Access Denied: External access to '/api/v1/internal/*' is blocked by ingress ACL policy."
        }), 403

# Response headers
@app.after_request
def security_headers(response):
    response.headers["Server"] = "APEX-Gateway/3.4 (CloudMesh)"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# Public Navigation Pages
@app.get("/")
def home():
    return render_template("index.html", tab="overview")

@app.get("/services")
def services_page():
    return render_template("index.html", tab="services")

@app.get("/api-docs")
def api_docs_page():
    return render_template("index.html", tab="docs")

@app.get("/telemetry")
def telemetry_page():
    return render_template("index.html", tab="telemetry")

@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "gateway": "active", "mesh_link": "connected"})

@app.get("/static/images/<path:filename>")
def static_logo(filename):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
    file_path = os.path.join(static_dir, filename)
    if os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        mimetype = "image/webp" if filename.endswith(".webp") else "image/png"
        return Response(data, mimetype=mimetype)
    return jsonify({"error": "File not found"}), 404

# Public Cluster API
@app.get("/api/v1/cluster/status")
def cluster_status():
    return jsonify({
        "status": "operational",
        "cluster_name": "rta-apex-prod-01",
        "region": "ap-south-1",
        "nodes_online": 8,
        "ingress_gateway": "online",
        "mesh_encryption": "active"
    })

@app.get("/api/v1/cluster/nodes")
def cluster_nodes():
    return jsonify({
        "status": "success",
        "nodes": [
            {"id": "node-worker-01", "ip": "10.244.1.12", "status": "Ready", "role": "worker"},
            {"id": "node-worker-02", "ip": "10.244.1.13", "status": "Ready", "role": "worker"},
            {"id": "node-control-01", "ip": "10.244.0.10", "status": "Ready", "role": "master"}
        ]
    })

# Unhardened Internal Management / Actuator Endpoint (VULNERABILITY #2)
@app.get("/api/v1/internal/env")
def internal_env():
    return jsonify({
        "status": "success",
        "cluster_profile": "production",
        "gateway_routing": {
            "public_prefix": "/api/v1/cluster",
            "internal_mesh_prefix": "/api/v1/internal"
        },
        "services": {
            "auth-gateway": {
                "version": "1.4.2",
                "endpoint": "http://10.244.0.10:8081",
                "status": "healthy"
            },
            "vault-enclave": {
                "version": "3.0.0",
                "endpoint": "/api/v1/internal/vault/keys",
                "description": "Air-gapped Master Vault Controller",
                "auth_mechanism": "HMAC-SHA256 Signed Gateway Header",
                "signing_header": "X-Cluster-Gateway-Signature",
                "identity_header": "X-Cluster-Identity",
                "timestamp_header": "X-Cluster-Timestamp",
                "signing_format": "{timestamp}.{method}.{path}",
                "shared_secret": INTERNAL_MESH_SECRET,
                "required_identity": "cluster_super_admin"
            }
        }
    })

# Air-Gapped Vault Controller (VULNERABILITY #3)
@app.get("/api/v1/internal/vault/keys")
def vault_keys():
    identity = request.headers.get("X-Cluster-Identity", "").strip()
    timestamp = request.headers.get("X-Cluster-Timestamp", "").strip()
    signature = request.headers.get("X-Cluster-Gateway-Signature", "").strip()

    if not (identity and timestamp and signature):
        return jsonify({
            "status": "error",
            "error": "Missing service mesh authentication headers: X-Cluster-Identity, X-Cluster-Timestamp, and X-Cluster-Gateway-Signature are required."
        }), 401

    if identity != "cluster_super_admin":
        return jsonify({
            "status": "error",
            "error": f"Identity '{identity}' lacks Master Vault clearance (cluster_super_admin required)."
        }), 403

    try:
        ts_int = int(timestamp)
        # 10 minute skew allowance
        if abs(int(time.time()) - ts_int) > 600:
            return jsonify({
                "status": "error",
                "error": "Timestamp verification failed: Clock skew exceeded 600 seconds."
            }), 401
    except ValueError:
        return jsonify({"status": "error", "error": "Invalid X-Cluster-Timestamp format. Must be Unix epoch."}), 400

    # Calculate expected HMAC-SHA256 signature
    msg = f"{timestamp}.GET./api/v1/internal/vault/keys".encode()
    expected_sig = hmac.new(INTERNAL_MESH_SECRET.encode(), msg, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature.lower(), expected_sig.lower()):
        return jsonify({
            "status": "error",
            "error": "Cryptographic signature verification failed: Invalid X-Cluster-Gateway-Signature."
        }), 401

    return jsonify({
        "status": "success",
        "vault_status": "unlocked",
        "identity": "cluster_super_admin",
        "master_vault_key": DYNAMIC_FLAG,
        "flag": DYNAMIC_FLAG
    })

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
