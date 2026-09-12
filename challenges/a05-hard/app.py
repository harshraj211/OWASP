"""A05 Hard: Injection - Blind Server-Side Template Injection (SSTI & RCE).

Vulnerability:
The telemetry format diagnostic engine accepts format expressions and evaluates them
via Jinja2's render_template_string(). The output is never reflected back to the client (Blind SSTI).
An aggressive WAF filter blacklists dots, underscores, square brackets, and classic SSTI keywords.
Attackers must craft an attribute-traversal payload using Jinja2 filters (|attr, |format)
and leverage an error-based or boolean oracle (e.g. {{1/0}} on False) to leak the dynamic flag
from /flag.txt character-by-character.
"""

import os
import secrets
from flask import Flask, request, render_template, render_template_string, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a05-hard"

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

try:
    with open("/flag.txt", "w") as f:
        f.write(DYNAMIC_FLAG)
except Exception:
    pass

# Hardened Blacklist
BLACKLIST = [
    "_", ".", "[", "]",
    "class", "mro", "base", "subclasses",
    "config", "self", "request", "import",
    "builtins", "os", "system", "popen",
    "subprocess", "read", "write", "open"
]

def waf_check(payload: str):
    payload_lower = payload.lower()
    for item in BLACKLIST:
        if item in payload_lower:
            return False, item
    return True, None

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "nginx/1.24.0 (Ubuntu)"
    return response

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/telemetry/probe", methods=["POST"])
def probe():
    data = request.get_json(silent=True) or request.form
    query = data.get("format", "")

    if not query:
        return jsonify({"status": "error", "message": "Missing 'format' parameter."}), 400

    passed, blocked_token = waf_check(query)
    if not passed:
        return jsonify({
            "status": "blocked",
            "message": f"Security WAF Alert: Prohibited token '{blocked_token}' detected in expression."
        }), 403

    try:
        # Blind Template Evaluation
        render_template_string(query)
        return jsonify({
            "status": "success",
            "message": "Telemetry format validated successfully by telemetry parser."
        }), 200
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Format parser syntax error."
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "6015"))
    app.run(host="0.0.0.0", port=port, debug=False)
