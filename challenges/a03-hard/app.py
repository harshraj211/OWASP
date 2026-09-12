"""A03 Hard: Software Supply Chain Failures - Enterprise SIEM Log4Shell / JNDI Supply Chain Attack.

Realistic Enterprise Scenario:
KubeShield Enterprise Cloud SIEM Gateway ingests audit events from microservice nodes.
Traffic passes through an Edge WAF enforcing strict CRS rules against common Log4Shell signatures:
- Direct JNDI scheme patterns
- Direct ${env: / ${sys: / ${java: expressions
- Simple single-character lower/upper transformations (${lower:j}, ${lower:e})
- Simple single-character fallback syntax (${::-j}, ${::-e})

Downstream, logs are forwarded to an asynchronous enterprise logging engine (Log4j Core).
An attacker must employ advanced multi-character folding, variable default fallbacks (${opt:-env}, ${var:-j}),
or nested multi-byte lookups (${lower:en}v:FLAG) to evade the edge WAF.
Furthermore, the ingestion endpoint processes events asynchronously (returning 202 Accepted);
the attacker must monitor the SIEM Live Audit Stream (/api/v1/audit/logs) to recover the evaluated flag.
"""

import os
import re
import secrets
from datetime import datetime
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a03-hard"
PORT = int(os.environ.get("LAB_PORT", 6009))

def get_flag():
    env_flag = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if env_flag:
        return env_flag.strip()
    if os.path.exists("/flag.txt"):
        try:
            with open("/flag.txt", "r") as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

for flag_path in [
    "/flag.txt",
    "/tmp/flag.txt",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag.txt"),
]:
    try:
        with open(flag_path, "w") as f:
            f.write(DYNAMIC_FLAG + "\n")
    except Exception:
        pass

os.environ["FLAG"] = DYNAMIC_FLAG

# Strict Enterprise WAF Filter
WAF_RULES = [
    re.compile(r"\$\{\s*jndi\s*:", re.IGNORECASE),
    re.compile(r"jndi\s*:\s*(ldap|rmi|dns|iiop|corba)", re.IGNORECASE),
    re.compile(r"\$\{\s*(env|sys|java)\s*:", re.IGNORECASE),
    re.compile(r"\$\{\s*(lower|upper)\s*:\s*[jndie]\s*\}", re.IGNORECASE),
    re.compile(r"\$\{\s*(lower|upper)\s*:\s*(jndi|env)\s*\}", re.IGNORECASE),
    re.compile(r"\$\{\s*::-[jndie]\s*\}", re.IGNORECASE),
]

SIEM_AUDIT_LOGS = [
    {
        "id": 9180,
        "timestamp": "2026-09-12 04:50:00",
        "level": "INFO",
        "source": "ingress-controller-us-east",
        "client_ip": "10.244.0.12",
        "event": "mTLS handshake verified for node-pool-finance-01",
        "context": "cluster=k8s-prod; proto=HTTP/2"
    },
    {
        "id": 9181,
        "timestamp": "2026-09-12 04:51:14",
        "level": "INFO",
        "source": "api-gateway-auth",
        "client_ip": "10.244.1.88",
        "event": "Service account token rotated for telemetry-exporter",
        "context": "scope=read:telemetry; issuer=vault.corp"
    }
]

def eval_lookup(expr, depth=0):
    if depth > 10:
        return expr

    if ":-" in expr:
        key, default = expr.split(":-", 1)
        if key == "" or key.startswith("::"):
            return default
        resolved_key = eval_lookup(key, depth + 1)
        if not resolved_key or resolved_key == key:
            return default
        return resolved_key

    if ":" in expr:
        prefix, val = expr.split(":", 1)
        p_low = prefix.lower()
        if p_low == "lower":
            return val.lower()
        if p_low == "upper":
            return val.upper()
        if p_low == "env":
            if val.upper() == "FLAG":
                return DYNAMIC_FLAG
            return os.environ.get(val, "")
        if p_low == "sys":
            if val.lower() in ["os.name", "os"]:
                return "Linux"
            return os.environ.get(val, f"sys-{val}")
        if p_low == "date":
            return datetime.now().strftime("%Y-%m-%d")
        if p_low == "jndi":
            if "127.0.0.1" in val or "localhost" in val or "flag" in val.lower():
                return f"[JNDI Directory Resource: {DYNAMIC_FLAG}]"
            return f"[JNDI: {val}]"
    return ""

def resolve_log4j(text, max_iter=12):
    pattern = re.compile(r"\$\{([^${}]+)\}")
    for _ in range(max_iter):
        match = pattern.search(text)
        if not match:
            break
        expr = match.group(1)
        replacement = eval_lookup(expr)
        text = text[:match.start()] + str(replacement) + text[match.end():]
    return text

@app.after_request
def add_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "KubeShield-SIEM-Ingress/4.2"
    return response

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/v1/audit/logs", methods=["GET"])
def get_logs():
    return jsonify({"success": True, "logs": SIEM_AUDIT_LOGS[:30]})

@app.route("/api/v1/telemetry/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "cluster": "kubeshield-prod-mesh",
        "active_nodes": 16,
        "waf_engine": "OWASP CRS v3.3.4 (Strict Rule Set)",
        "logging_backend": "Enterprise Telemetry Ingestion Core (Async)",
        "events_processed": len(SIEM_AUDIT_LOGS) + 5240
    })

@app.route("/api/v1/telemetry/ingest", methods=["POST"])
def ingest_telemetry():
    audit_context = request.headers.get("X-Audit-Context", "")
    forwarded_for = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
    user_agent = request.headers.get("User-Agent", "Cluster-Telemetry-Client/2.0")

    body_data = request.get_json() or {}
    event_message = str(body_data.get("event", "")).strip()
    source_component = str(body_data.get("source", "mesh-gateway")).strip()
    custom_context = str(body_data.get("context", "")).strip()

    combined_context = audit_context or custom_context or f"client={forwarded_for}; ua={user_agent[:30]}"
    candidate_text = f"{event_message} {combined_context} {user_agent}"

    # Edge WAF Inspection
    for r in WAF_RULES:
        if r.search(candidate_text):
            return jsonify({
                "success": False,
                "blocked": True,
                "error": "403 Forbidden: WAF Rule Triggered — Signature matched prohibited keyword pattern."
            }), 403

    # Asynchronous Ingestion & Downstream Evaluation
    resolved_message = resolve_log4j(event_message or f"Event from {forwarded_for}")
    resolved_context = resolve_log4j(combined_context)

    log_id = len(SIEM_AUDIT_LOGS) + 9180
    log_entry = {
        "id": log_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": "INFO" if not ("RTSA{" in resolved_message or "RTSA{" in resolved_context) else "ALERT",
        "source": source_component,
        "client_ip": forwarded_for,
        "event": resolved_message,
        "context": resolved_context
    }
    SIEM_AUDIT_LOGS.insert(0, log_entry)

    # Realistic Enterprise Behavior: Response is 202 Accepted, flag is ONLY in the audit stream
    return jsonify({
        "success": True,
        "status": "QUEUED",
        "event_id": log_id,
        "message": "Telemetry event accepted and queued for downstream SIEM batch processing."
    }), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
