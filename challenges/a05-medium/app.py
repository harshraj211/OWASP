"""A05 Medium: Injection - Server-Side Request Forgery (SSRF) & DNS Validation Bypass.

Vulnerability:
The WebPulse URL availability inspector attempts to block internal network access by
resolving hostnames to IP addresses and checking against loopback and RFC 1918 private ranges.
However, the HTTP client (urllib.request.urlopen) blindly follows HTTP redirects (301/302).
Attackers can bypass this Time-of-Check to Time-of-Use (TOCTOU) DNS validation by pointing
the inspector to an external redirect service or local relay endpoint that redirects to
http://127.0.0.1:<PORT>/admin/status to steal the internal sovereign vault flag.
"""

import os
import secrets
import socket
import ipaddress
import urllib.request
import urllib.error
import urllib.parse
from flask import Flask, request, render_template, jsonify, redirect

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a05-medium"

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

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "nginx/1.24.0 (Ubuntu)"
    return response

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

# Local relay endpoint for offline environments
@app.route("/relay", methods=["GET"])
def relay():
    target = request.args.get("target", "")
    if target:
        return redirect(target, code=302)
    return jsonify({"error": "Missing target parameter"}), 400

@app.route("/", methods=["GET"])
def index():
    target_url = request.args.get("url", "").strip()
    if not target_url:
        return render_template("index.html", target_url="", result=None)

    # DNS Validation Check
    try:
        parsed_url = urllib.parse.urlparse(target_url)
        hostname = parsed_url.hostname
        if not hostname:
            return render_template("index.html", target_url=target_url, result="[ACCESS DENIED] Invalid or malformed URL structure.")

        # Resolve hostname to IPv4
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)

        # Block loopback, private, or unspecified IP addresses
        if ip_obj.is_loopback or ip_obj.is_private or ip == "0.0.0.0":
            return render_template(
                "index.html",
                target_url=target_url,
                result=f"[ACCESS DENIED] Strict Network Policy: Prohibited internal/loopback destination (Resolved IP: {ip})."
            )
    except Exception as e:
        return render_template("index.html", target_url=target_url, result=f"[ACCESS DENIED] DNS Resolution failed: {str(e)}")

    # Fetch endpoint using urllib.request (blindly follows HTTP redirects)
    try:
        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "RedTeam-Security-Probe/3.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return render_template("index.html", target_url=target_url, result=content[:3000])
    except urllib.error.HTTPError as e:
        body_snippet = e.read().decode("utf-8", errors="replace")[:1000]
        return render_template("index.html", target_url=target_url, result=f"[PROBE HTTP {e.code}] {e.reason}\n\n{body_snippet}")
    except Exception as e:
        return render_template("index.html", target_url=target_url, result=f"[PROBE ERROR] Connection failed: {str(e)}")

@app.route("/admin/status", methods=["GET"])
def admin_status():
    remote_ip = request.remote_addr
    # Only loopback callers allowed
    if remote_ip not in ["127.0.0.1", "::1", "localhost"]:
        return jsonify({
            "status": "error",
            "message": f"Security Exception: Restricted to internal loopback service mesh. (Your IP: {remote_ip})"
        }), 403

    return jsonify({
        "status": "authorized",
        "service": "Internal Sovereign Vault Master Node",
        "flag": DYNAMIC_FLAG
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "6014"))
    app.run(host="0.0.0.0", port=port, debug=False)
