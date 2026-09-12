import os
import subprocess
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'redteam_hacker_academy_oswap_secret_key_2026'

DEFAULT_USER = "redteamacademy"
DEFAULT_PASS = "redteamacademy"

# OWASP Top 10 2025 Web Security Standard — 30 Unique Challenges (3 per Category)
OWASP_CATEGORIES_2025 = [
    {
        "id": "A01",
        "code": "A01:2025",
        "title": "Broken Access Control",
        "description": "Access control enforces policy so users cannot act outside intended permissions, including SSRF and CORS flaws.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Horizontal Privilege Escalation (IDOR)",
                "topic": "IDOR, Parameter Tampering, REST API",
                "cmd_code": "A01 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "MeridianHR Vertical Privilege Escalation",
                "topic": "Missing Function-Level Access Control, Forced Browsing, Workflow Bypass",
                "cmd_code": "A01 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Asterion Benefits Exchange",
                "topic": "CORS, Origin Reflection, Credentialed Cross-Origin Data Exposure",
                "cmd_code": "A01 hard"
            }
        ]
    },
    {
        "id": "A02",
        "code": "A02:2025",
        "title": "Security Misconfiguration",
        "description": "Insecure default settings, exposed sensitive files/interfaces, and reverse proxy or cache misconfigurations.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Exposed Sensitive Files & Debug Console",
                "topic": "Git Exposure, Env File Leak, Debug Console",
                "cmd_code": "A02 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Nginx Off-by-Slash & Reverse Proxy Traversal",
                "topic": "Reverse Proxy Misconfiguration, Alias Traversal, Internal Bypass",
                "cmd_code": "A02 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Web Cache Deception & Request Smuggling",
                "topic": "Cache Rules Misconfiguration, WCD, Hop-by-Hop Headers, CL.TE",
                "cmd_code": "A02 hard"
            }
        ]
    },
    {
        "id": "A03",
        "code": "A03:2025",
        "title": "Software Supply Chain Failures",
        "description": "Risks from compromised dependencies, untrusted third-party packages, vulnerable components, and build pipeline flaws.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Known Component CVE Exploitation",
                "topic": "Known Component CVE, Dependency Audit, Framework Exploit",
                "cmd_code": "A03 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Dependency Confusion & Poisoned Package",
                "topic": "Package Registry Confusion, Namespace Hijacking, Malicious Script",
                "cmd_code": "A03 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Log4Shell / JNDI Supply Chain Attack",
                "topic": "Log4Shell, JNDI Remote Class Loading, Untrusted Logging, RCE",
                "cmd_code": "A03 hard"
            }
        ]
    },
    {
        "id": "A04",
        "code": "A04:2025",
        "title": "Cryptographic Failures",
        "description": "Failures related to cryptography exposing sensitive data, weak ciphers, and flawed token validations.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "JWT Key Traversal & Signature Bypass",
                "topic": "JWT, Key ID (kid) Path Traversal, HS256 Signature Forgery",
                "cmd_code": "A04 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Cryptographic Hash Length Extension",
                "topic": "Merkle-Damgard, SHA-256 MAC Extension, Integrity Tampering",
                "cmd_code": "A04 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "AES-256-CBC Padding Oracle Attack",
                "topic": "AES-CBC, PKCS#7 Side-Channel, Byte-by-Byte Decryption & Forgery",
                "cmd_code": "A04 hard"
            }
        ]
    },
    {
        "id": "A05",
        "code": "A05:2025",
        "title": "Injection",
        "description": "Applications fail to sanitize user-supplied input across SQL, command, LDAP, and client-side interpreters.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "SQL Injection Authentication Bypass",
                "topic": "SQLite Auth Bypass, WAF Evasion (No Spaces/Comments), Subqueries & GLOB",
                "cmd_code": "A05 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Server-Side Request Forgery (SSRF)",
                "topic": "SSRF, Pre-Flight DNS Validation Bypass, HTTP 302 Redirection & TOCTOU",
                "cmd_code": "A05 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Blind Server-Side Template Injection (SSTI)",
                "topic": "Jinja2 Sandbox Escape, Blacklist Filter Evasion, Blind Boolean Oracle",
                "cmd_code": "A05 hard"
            }
        ]
    },
    {
        "id": "A06",
        "code": "A06:2025",
        "title": "Insecure Design",
        "description": "Flaws in architectural design, business logic workflows, and failure to apply threat modeling.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Password Reset Poisoning",
                "topic": "Host Header Injection, Password Reset Hijacking",
                "cmd_code": "A06 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Cross-Site Request Forgery (CSRF)",
                "topic": "CSRF, State-Changing Requests, Missing Anti-CSRF Token",
                "cmd_code": "A06 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Business Logic Abuse",
                "topic": "Multi-Step Cart Logic, Coupon Stacking, Negative Cart",
                "cmd_code": "A06 hard"
            }
        ]
    },
    {
        "id": "A07",
        "code": "A07:2025",
        "title": "Authentication Failures",
        "description": "Failures in identity verification, credential handling, session management, and multi-factor authentication.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Weak Password Policy",
                "topic": "Credential Guessing, Password Spraying, Legacy Policy Bypass",
                "cmd_code": "A07 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "MFA Bypass",
                "topic": "Improper MFA Validation, Step Jumping, Session Elevation",
                "cmd_code": "A07 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Password Reset Token Prediction",
                "topic": "Predictable PRNG Tokens, Seed Recovery, Account Takeover",
                "cmd_code": "A07 hard"
            }
        ]
    },
    {
        "id": "A08",
        "code": "A08:2025",
        "title": "Software or Data Integrity Failures",
        "description": "Applications failing to verify the integrity of critical data, untrusted deserialization, and unvalidated updates.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Unsigned Plugin Installation",
                "topic": "Untrusted Code Execution, Signature Verification Bypass, Malicious Plugin",
                "cmd_code": "A08 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Insecure Update Mechanism",
                "topic": "Unauthenticated Update Packages, Checksum Tampering, Firmware Hijack",
                "cmd_code": "A08 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Unsafe Deserialization",
                "topic": "Restricted Object Deserialization, Python Gadget Chain, Arbitrary Code Execution",
                "cmd_code": "A08 hard"
            }
        ]
    },
    {
        "id": "A09",
        "code": "A09:2025",
        "title": "Security Logging and Alerting Failures",
        "description": "Insufficient logging, lack of real-time monitoring and alerting, and exploiting logging sinks as attack vectors.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Missing Login Logs",
                "topic": "Unlogged Authentication Routes, SIEM Evasion, Brute Force Detection Failure",
                "cmd_code": "A09 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Log Injection",
                "topic": "CRLF Injection, Log Forgery, Automated Audit Daemon Deception",
                "cmd_code": "A09 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Audit Log Tampering",
                "topic": "Audit Ledger Manipulation, Chained Hash Reconstruction, Evidence Tampering",
                "cmd_code": "A09 hard"
            }
        ]
    },
    {
        "id": "A10",
        "code": "A10:2025",
        "title": "Mishandling of Exceptional Conditions",
        "description": "Security risks arising when applications fail to safely handle unexpected runtime errors, failing open, or leaking system internals.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Information Disclosure Through Errors",
                "topic": "Unhandled Exceptions, Stack Traces, Internal File Paths & Token Leak",
                "cmd_code": "A10 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Unhandled Exception Denial of Service",
                "topic": "Malformed Input Exception, State Machine Crash, Fail-Open Override",
                "cmd_code": "A10 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "File Upload Validation Bypass",
                "topic": "Image Parser Crash, Exception Mishandling Fail-Open, Web Shell Upload to RCE",
                "cmd_code": "A10 hard"
            }
        ]
    }
]

@app.before_request
def enforce_login():
    if not session.get('logged_in'):
        if request.endpoint and request.endpoint.startswith('api_') or request.path.startswith('/api/'):
            # Allow API endpoints to check status or return proper json
            if request.endpoint not in ['lab_status', 'submit_flag']:
                return jsonify({"success": False, "error": "Unauthorized. Please log in."}), 401
        elif request.endpoint not in ['login', 'static']:
            return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'), code=303)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == DEFAULT_USER and password == DEFAULT_PASS:
            session['logged_in'] = True
            session['username'] = username
            flash("Welcome to RedTeam Hacker Academy Portal!", "success")
            return redirect(url_for('index'), code=303)
        else:
            flash("Login Failed: Incorrect Username or Password!", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/labs')
def labs():
    return render_template('labs.html', categories=OWASP_CATEGORIES_2025)

@app.route('/labs/<cat_id>')
def lab_detail(cat_id):
    category = next((c for c in OWASP_CATEGORIES_2025 if c['id'].lower() == cat_id.lower()), None)
    if not category:
        flash("Category not found.", "error")
        return redirect(url_for('labs'))
    return render_template('lab_detail.html', category=category)

import json

@app.route('/api/lab-status', methods=['GET'])
def lab_status():
    status_file = "/tmp/active_lab.json"
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as f:
                data = json.load(f)
            # Verify if container is actually running
            res = subprocess.run(["docker", "ps", "-q", "-f", "name=oswap-active-challenge"], capture_output=True, text=True)
            if res.stdout.strip():
                return jsonify({
                    "running": True,
                    "challenge": data.get("challenge"),
                    "port": data.get("port", 6001)
                })
            if data.get("mode") == "process":
                pid = data.get("pid")
                if isinstance(pid, int) and subprocess.run(["kill", "-0", str(pid)], capture_output=True).returncode == 0:
                    return jsonify({"running": True, "challenge": data.get("challenge"), "port": data.get("port", 6001)})
        except Exception:
            pass
    return jsonify({"running": False})

@app.route('/api/launch-lab', methods=['POST'])
def launch_lab():
    data = request.get_json() or {}
    cmd_code = data.get('cmd_code')
    if not cmd_code:
        return jsonify({"success": False, "error": "Invalid lab selection"}), 400

    try:
        parts = cmd_code.split()
        category = parts[0]
        level = parts[1]
        target_challenge = f"{category.lower()}-{level.lower()}"
        status_file = "/tmp/active_lab.json"

        # Check if this lab is already running to avoid unnecessary restarts
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    active_info = json.load(f)
                if active_info.get("running") and active_info.get("challenge") == target_challenge:
                    docker_check = subprocess.run(["docker", "ps", "-q", "-f", "name=oswap-active-challenge"], capture_output=True, text=True)
                    if docker_check.stdout.strip() or active_info.get("mode") == "process":
                        return jsonify({
                            "success": True,
                            "already_running": True,
                            "message": f"Lab {category} ({level}) is already running on port {active_info.get('port', 6001)}",
                            "port": active_info.get("port", 6001),
                            "challenge": target_challenge
                        })
            except Exception:
                pass

        launcher_script = os.path.join(app.root_path, "scripts", "start_challenge.sh")
        if os.path.exists(launcher_script):
            subprocess.run([launcher_script, category, level], check=True)
            port = 6001
            status_file = "/tmp/active_lab.json"
            if os.path.exists(status_file):
                try:
                    with open(status_file, "r") as f:
                        lab_info = json.load(f)
                    port = lab_info.get("port", 6001)
                except Exception:
                    pass
            return jsonify({
                "success": True, 
                "message": f"Lab {category} ({level}) started on port {port}",
                "port": port,
                "challenge": f"{category.lower()}-{level.lower()}"
            })
        else:
            return jsonify({"success": False, "error": "Launcher script not found"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/submit-flag', methods=['POST'])
def submit_flag():
    data = request.get_json() or {}
    submitted_flag = data.get('flag', '').strip()
    status_file = "/tmp/active_lab.json"

    if not os.path.exists(status_file):
        return jsonify({"success": False, "error": "No lab is currently running. Please launch the lab first."}), 400

    try:
        with open(status_file, "r") as f:
            lab_data = json.load(f)
        correct_flag = lab_data.get("flag", "")

        if submitted_flag and submitted_flag == correct_flag:
            return jsonify({
                "success": True,
                "message": "Correct flag! Challenge Solved successfully."
            })
        else:
            return jsonify({
                "success": False,
                "message": "Incorrect flag. Please try again."
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stop-lab', methods=['POST'])
def stop_lab():
    try:
        docker_result = subprocess.run(["docker", "rm", "-f", "oswap-active-challenge"], capture_output=True, text=True)
        if os.path.exists("/tmp/oswap-active-challenge.pid"):
            with open("/tmp/oswap-active-challenge.pid", "r") as f:
                pid = f.read().strip()
            if pid.isdigit():
                subprocess.run(["kill", pid], capture_output=True)
            os.remove("/tmp/oswap-active-challenge.pid")
        if os.path.exists("/tmp/active_lab.json"):
            os.remove("/tmp/active_lab.json")
        remaining = subprocess.run(["docker", "ps", "-q", "-f", "name=oswap-active-challenge"], capture_output=True, text=True)
        if remaining.stdout.strip():
            return jsonify({"success": False, "error": "The lab container could not be stopped."}), 500
        return jsonify({"success": True, "message": "Lab stopped successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("RedTeam Hacker Academy Authentication System running on http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
