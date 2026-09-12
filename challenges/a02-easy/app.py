"""A02 easy: Security Misconfiguration - Production Cluster Portal.

The portal functions as a normal enterprise cluster console.
A classic deployment mistake: developers synced the repository into the web document root,
leaving the version control metadata (.git) accessible.
"""

import os
import secrets
from flask import Flask, jsonify, render_template, request, send_file, Response

app = Flask(__name__)

def instance_flag() -> str:
    configured_flag = os.environ.get("FLAG", "").strip()
    if configured_flag:
        return configured_flag
    return f"RTSA{{a02_easy_misconfig_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = instance_flag()
VAULT_API_TOKEN = "RTA_CLUSTER_VAULT_KEY_e98f71c4"

GIT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_git")

@app.after_request
def add_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "nginx/1.24.0 (Ubuntu)"
    return response

# Clean Navigation Routes
@app.get("/")
def index():
    return render_template("index.html", tab="overview")

@app.get("/clusters")
def clusters():
    return render_template("index.html", tab="clusters")

@app.get("/nodes")
def nodes():
    return render_template("index.html", tab="nodes")

@app.get("/metrics")
def metrics():
    return render_template("index.html", tab="metrics")

@app.get("/settings")
def settings():
    return render_template("index.html", tab="settings")

@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})

# Serving authentic Git files from repo_git
@app.get("/.git/<path:subpath>")
def serve_git_subpath(subpath: str):
    file_path = os.path.normpath(os.path.join(GIT_DIR, subpath))
    if file_path.startswith(GIT_DIR) and os.path.isfile(file_path):
        return send_file(file_path, mimetype="application/octet-stream")
    return "404 Not Found", 404

@app.get("/.git/")
@app.get("/.git/HEAD")
def serve_git_head():
    head_path = os.path.join(GIT_DIR, "HEAD")
    if os.path.isfile(head_path):
        return send_file(head_path, mimetype="text/plain")
    return "404 Not Found", 404

# Normal public endpoints
@app.get("/api/v1/clusters")
def api_clusters():
    return jsonify({
        "clusters": [
            {"id": "rtsa-prod-k8s-01", "role": "Control Plane", "nodes": 3, "status": "active"},
            {"id": "rtsa-worker-pool", "role": "Training Pods", "nodes": 8, "status": "active"},
            {"id": "rtsa-vault-sync", "role": "Compliance Vault", "nodes": 1, "status": "restricted"}
        ]
    })

@app.get("/api/v1/metrics")
def api_metrics():
    return jsonify({
        "cpu_utilization": "28.4%",
        "memory_used_gb": 42.8,
        "active_training_pods": 84,
        "network_ingress_mbps": 114.2
    })

# Hidden Vault Endpoint - only discovered by inspecting config.json from git objects
@app.route("/api/v1/internal/vault/keys", methods=["GET", "POST"])
def internal_vault_keys():
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif "X-Vault-Token" in request.headers:
        token = request.headers.get("X-Vault-Token", "").strip()

    if not token:
        return jsonify({
            "status": "error",
            "error": "Unauthorized: Missing Bearer token in Authorization header."
        }), 401

    if token != VAULT_API_TOKEN:
        return jsonify({
            "status": "error",
            "error": "Forbidden: Provided vault key is revoked or invalid."
        }), 403

    return jsonify({
        "status": "success",
        "cluster": "rtsa-vault-sync",
        "zone": "internal-compliance-vault",
        "flag": DYNAMIC_FLAG,
        "secrets": {
            "root_db": "postgres://auditor:k8s_m@st3r_9981@10.240.4.51:5432/compliance",
            "flag": DYNAMIC_FLAG
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "6004"))
    app.run(host="0.0.0.0", port=port, debug=False)
