"""A04 Medium: Cryptographic Failures - Hash Length Extension Attack.

Vulnerability:
The application uses an insecure Message Authentication Code (MAC) construction:
    MAC = SHA256(SECRET || data)
Because SHA-256 uses the Merkle-Damgard construction, an attacker who knows the length
of the secret (16 bytes) and the MAC of a known message can append arbitrary data
(including null bytes and path components like 'flag.txt') and compute the new valid MAC
without knowing the secret.
"""

import os
import secrets
import hashlib
import urllib.parse
from flask import Flask, request, render_template, jsonify, Response

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a04-medium"

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

# 16-byte secret key for HMAC/MAC generation
MAC_SECRET = secrets.token_hex(8).encode()

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

@app.route("/", methods=["GET"])
def home():
    filename = b"public_report.pdf"
    valid_mac = hashlib.sha256(MAC_SECRET + filename).hexdigest()
    return render_template("index.html", valid_mac=valid_mac, default_file="public_report.pdf")

@app.route("/download", methods=["GET"])
def download():
    raw_query = request.query_string
    mac = request.args.get("mac", "").strip()

    file_bytes = b""
    for param in raw_query.split(b"&"):
        if param.startswith(b"file="):
            file_bytes = urllib.parse.unquote_to_bytes(param[5:])
            break

    if not file_bytes or not mac:
        return render_template("index.html", error="Missing 'file' or 'mac' query parameter.")

    expected_mac = hashlib.sha256(MAC_SECRET + file_bytes).hexdigest()

    # Constant time verification
    if not secrets.compare_digest(mac.lower(), expected_mac.lower()):
        return render_template("index.html", error="Cryptographic Integrity Fault: Invalid MAC signature. Tampering detected!")

    safe_filename = file_bytes.split(b"\x00")[-1].decode(errors="ignore")

    if "flag.txt" in safe_filename or b"flag.txt" in file_bytes:
        return Response(DYNAMIC_FLAG, mimetype="text/plain")

    if safe_filename == "public_report.pdf" or file_bytes == b"public_report.pdf":
        report_content = "RedTeam Hacker Academy: Sovereign Cloud Security Architecture Assessment - Q3 Report (Public Release)."
        return Response(report_content, mimetype="text/plain")

    return render_template("index.html", error=f"Target file '{safe_filename}' does not exist on vault repository.")

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "6011"))
    app.run(host="0.0.0.0", port=port, debug=False)
