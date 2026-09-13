"""A02 medium: Security Misconfiguration - Nginx Off-by-Slash & Reverse Proxy Traversal.

Vulnerability Mechanics:
1. Emulates Nginx alias path traversal:
   `location /static { alias /app/static/; }`
   Because /static lacks a trailing slash, requesting `/static../internal_config.py` resolves to `/app/internal_config.py`.
2. Leaking `internal_config.py` discloses `X-Internal-Gateway-Key` and the hidden endpoint `/api/v1/internal/compliance/audit-vault`.
3. Supplying this header to the hidden endpoint returns the dynamic flag.
"""

import os
import secrets
from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

def instance_flag() -> str:
    configured_flag = os.environ.get("FLAG", "").strip()
    if configured_flag:
        return configured_flag
    return f"RTSA{{a02_medium_alias_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = instance_flag()
INTERNAL_AUTH_SECRET = "RTA_SEC_INTERNAL_GATEWAY_BYPASS_9918"

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "nginx/1.25.3 (Ubuntu)"
    return response

# Clean Navigation Routes (No 404s!)
@app.get("/")
def home():
    return render_template("index.html", tab="overview")

@app.get("/assets")
def assets():
    return render_template("index.html", tab="assets")

@app.get("/teams")
def teams():
    return render_template("index.html", tab="teams")

@app.get("/settings")
def settings():
    return render_template("index.html", tab="settings")

@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "proxy": "nginx/1.25.3"})

# Exact Nginx off-by-slash alias emulation:
# location /static { alias /app/static/; }
@app.route("/static<path:subpath>")
def nginx_alias_handler(subpath):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_root = os.path.join(base_dir, "static")
    
    if subpath.startswith("/"):
        resolved_path = os.path.normpath(os.path.join(static_root, subpath.lstrip("/")))
    else:
        # Off-by-slash: /static../internal_config.py -> /app/static/ + "../internal_config.py"
        raw_combined = static_root + "/" + subpath
        resolved_path = os.path.normpath(raw_combined)

    if os.path.exists(resolved_path) and os.path.isfile(resolved_path):
        mimetype = "text/plain"
        if resolved_path.endswith(".webp"):
            mimetype = "image/webp"
        elif resolved_path.endswith(".png"):
            mimetype = "image/png"
        elif resolved_path.endswith(".css"):
            mimetype = "text/css"
        elif resolved_path.endswith(".py"):
            mimetype = "text/x-python"
        return send_file(resolved_path, mimetype=mimetype)
    
    return "404 Not Found", 404

# Hidden Compliance Vault Endpoint - Discovered by leaking internal_config.py
@app.route("/api/v1/internal/compliance/audit-vault", methods=["GET", "POST"])
def compliance_vault():
    auth_key = None
    if "X-Internal-Gateway-Key" in request.headers:
        auth_key = request.headers.get("X-Internal-Gateway-Key", "").strip()
    elif request.is_json:
        auth_key = request.json.get("key", "").strip()
    elif request.args.get("key"):
        auth_key = request.args.get("key", "").strip()

    if not auth_key:
        return jsonify({
            "status": "error",
            "error": "Access Denied: Missing internal cluster authorization header 'X-Internal-Gateway-Key'."
        }), 403

    if auth_key != INTERNAL_AUTH_SECRET:
        return jsonify({
            "status": "error",
            "error": "Forbidden: Provided X-Internal-Gateway-Key is invalid."
        }), 403

    return jsonify({
        "status": "success",
        "authorized": True,
        "zone": "internal-compliance-vault",
        "audit_officer": "Platform Security Officer",
        "flag": DYNAMIC_FLAG,
        "compliance_records": {
            "status": "Verified",
            "flag": DYNAMIC_FLAG
        }
    })

# Backwards compatibility alias for earlier endpoint
@app.route("/api/internal/system-vault", methods=["GET", "POST"])
def legacy_vault():
    return compliance_vault()

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or "6005")
    app.run(host="0.0.0.0", port=port, debug=False)
