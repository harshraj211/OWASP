"""A04 Easy: Cryptographic Failures - JWT Key Traversal & Signature Forgery.

Vulnerability:
The server parses the JWT 'kid' (Key ID) header without proper sanitization and uses
it as a file path relative to the 'keys/' directory. Attackers can traverse outside
the directory to reference a known empty or predictable file (e.g. /dev/null or /proc/sys/kernel/domainname),
enabling token forgery to achieve administrative access.
"""

import os
import secrets
import datetime
import jwt
from flask import Flask, request, render_template, redirect, make_response, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a04-easy"

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

KEYS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys")
os.makedirs(KEYS_DIR, exist_ok=True)
REAL_SECRET = secrets.token_hex(32)
with open(os.path.join(KEYS_DIR, "server_secret.key"), "w") as f:
    f.write(REAL_SECRET)

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
    token = request.cookies.get("auth_session")
    if token:
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid", "server_secret.key")

            # Vulnerable Key Resolution via Path Traversal
            key_path = os.path.join(KEYS_DIR, kid)
            try:
                with open(key_path, "r") as f:
                    secret = f.read().strip()
            except Exception:
                secret = secrets.token_hex(16)

            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            user = decoded.get("user")
            role = decoded.get("role")
            return render_template("index.html", user=user, role=role, flag=DYNAMIC_FLAG)
        except jwt.ExpiredSignatureError:
            return render_template("index.html", error="Session token expired.")
        except jwt.InvalidTokenError:
            return render_template("index.html", error="Invalid cryptographic signature.")
        except Exception as e:
            return render_template("index.html", error=f"Authentication exception: {str(e)}")

    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if username == "guest" and password == "guest":
        payload = {
            "user": username,
            "role": "guest",
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
        }

        with open(os.path.join(KEYS_DIR, "server_secret.key"), "r") as f:
            secret = f.read().strip()

        token = jwt.encode(payload, secret, algorithm="HS256", headers={"kid": "server_secret.key"})
        resp = make_response(redirect("/"))
        resp.set_cookie("auth_session", token)
        return resp

    return render_template("index.html", error="Invalid credentials. Available account: guest / guest")

@app.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("auth_session")
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or "6010")
    app.run(host="0.0.0.0", port=port, debug=False)
