"""A04 Hard: Cryptographic Failures - AES-256-CBC PKCS#7 Padding Oracle Attack.

Vulnerability:
The web service authenticates users via an AES-CBC encrypted cookie. When decrypting,
the server responds differently depending on whether PKCS#7 padding was valid or invalid:
  - Invalid padding: returns 500 with "Decryption Error: Invalid padding bytes."
  - Valid padding, invalid JSON: returns 200 with "Session Error: Invalid JSON structure."
  - Valid padding, valid JSON: parses JSON and checks role.
This distinct error behavior forms a classic padding oracle, allowing attackers to
decrypt ciphertexts byte-by-byte and forge arbitrary encrypted blocks to become admin.
"""

import os
import json
import base64
import secrets
from flask import Flask, request, render_template, make_response, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a04-hard"

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

# 32-byte secret key for AES-256
AES_KEY = secrets.token_bytes(32)

try:
    with open("/flag.txt", "w") as f:
        f.write(DYNAMIC_FLAG)
except Exception:
    pass

def encrypt_cookie(data: str) -> str:
    iv = secrets.token_bytes(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode()

def decrypt_cookie(b64_data: str) -> str:
    raw = base64.b64decode(b64_data)
    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode()

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
    cookie = request.cookies.get("session_auth")

    if not cookie:
        payload = json.dumps({"role": "guest", "id": secrets.randbelow(1000)})
        new_cookie = encrypt_cookie(payload)
        resp = make_response(render_template("index.html", role="guest", cookie_val=new_cookie, msg="New encrypted session token provisioned."))
        resp.set_cookie("session_auth", new_cookie)
        return resp

    try:
        plaintext = decrypt_cookie(cookie)
    except ValueError as e:
        if "padding" not in str(e).lower():
            return render_template("index.html", error="Decryption Error: Malformed ciphertext.", cookie_val=cookie), 500
        # The Oracle response for padding failure
        return render_template("index.html", error="Decryption Error: Invalid padding bytes.", cookie_val=cookie), 500
    except Exception:
        return render_template("index.html", error="Decryption Error: Malformed ciphertext.", cookie_val=cookie), 500

    try:
        data = json.loads(plaintext)
    except json.JSONDecodeError:
        # The Oracle response for valid padding but malformed JSON
        return render_template("index.html", error="Session Error: Invalid JSON structure.", cookie_val=cookie), 200

    role = data.get("role", "unknown")
    if role == "admin":
        return render_template("index.html", role=role, flag=DYNAMIC_FLAG, cookie_val=cookie)

    return render_template("index.html", role=role, cookie_val=cookie)

@app.route("/reset", methods=["GET"])
def reset():
    resp = make_response(jsonify({"status": "reset"}))
    resp.delete_cookie("session_auth")
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("LAB_PORT", "6012"))
    app.run(host="0.0.0.0", port=port, debug=False)
