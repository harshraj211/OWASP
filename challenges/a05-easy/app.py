"""A05 Easy: Injection - SQL Injection Authentication Bypass (Hard WAF Filter).

Vulnerability:
The authentication endpoint concatenates user input directly into an SQL query:
  SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'
A strict Web Application Firewall (WAF) regex blocks whitespace (\s), all SQL comments (-- , #, /*, */),
boolean keywords (OR, AND), and comparison operators (=, LIKE).
Attackers can evade this filter using SQLite subqueries, GLOB operators, IN clauses,
and CHAR() functions to bypass authentication or extract credentials.
"""

import os
import re
import sqlite3
import secrets
from flask import Flask, request, render_template, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a05-easy"

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

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    admin_pass = secrets.token_hex(16)
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', ?, 'administrator')", (admin_pass,))
    c.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'user')")
    conn.commit()
    conn.close()

WAF_REGEX = re.compile(r"(\s|--|#|/\*|\*/|\bOR\b|\bAND\b|=|\bLIKE\b)", re.IGNORECASE)

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
    return render_template("index.html", flag=DYNAMIC_FLAG)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if WAF_REGEX.search(username) or WAF_REGEX.search(password):
        return render_template(
            "index.html",
            error="Security WAF Violation: Prohibited tokens or delimiters detected.",
            flag=DYNAMIC_FLAG
        )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            session["role"] = user[2]
            return redirect(url_for("home"))
        else:
            return render_template("index.html", error="Authentication failed: Invalid credentials.", flag=DYNAMIC_FLAG)
    except Exception:
        conn.close()
        return render_template("index.html", error="Database engine syntax fault.", flag=DYNAMIC_FLAG)

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("LAB_PORT", "6013"))
    app.run(host="0.0.0.0", port=port, debug=False)
