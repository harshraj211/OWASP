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
        "description": "Access control enforces policy so users cannot act outside intended permissions.",
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
                "name": "CORS Misconfiguration",
                "topic": "CORS, Origin Reflection, Cross-Origin Data Exfiltration",
                "cmd_code": "A01 hard"
            }
        ]
    },
    {
        "id": "A02",
        "code": "A02:2025",
        "title": "Cryptographic Failures",
        "description": "Failures related to cryptography exposing sensitive data and authentication tokens.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "JWT Algorithm Confusion",
                "topic": "JWT, None Algorithm, Signature Bypass",
                "cmd_code": "A02 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Weak Hash Cracking",
                "topic": "MD5, Database Dump, Rainbow Tables",
                "cmd_code": "A02 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Padding Oracle Attack",
                "topic": "AES-CBC, PKCS7, Padding Oracle, Cookie Forgery",
                "cmd_code": "A02 hard"
            }
        ]
    },
    {
        "id": "A03",
        "code": "A03:2025",
        "title": "Injection & Remote Execution",
        "description": "Applications fail to sanitize user-supplied input across client-side and server-side contexts.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Cross-Site Scripting (XSS)",
                "topic": "XSS, Reflected, Stored, WAF Bypass",
                "cmd_code": "A03 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "SQL Injection (SQLi)",
                "topic": "SQL Injection, Union-Based, Error-Based, Auth Bypass",
                "cmd_code": "A03 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "OS Command Injection",
                "topic": "Command Injection, RCE, Filename Injection, WAF Evasion",
                "cmd_code": "A03 hard"
            }
        ]
    },
    {
        "id": "A04",
        "code": "A04:2025",
        "title": "Insecure Design & Business Logic Flaws",
        "description": "Flaws in architectural design and workflow logic.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Password Reset Poisoning",
                "topic": "Host Header Injection, Password Reset Hijacking",
                "cmd_code": "A04 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Cross-Site Request Forgery (CSRF)",
                "topic": "CSRF, State-Changing Requests, Missing Anti-CSRF Token",
                "cmd_code": "A04 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Business Logic Abuse",
                "topic": "Multi-Step Cart Logic, Coupon Stacking, Negative Cart",
                "cmd_code": "A04 hard"
            }
        ]
    },
    {
        "id": "A05",
        "code": "A05:2025",
        "title": "Security Misconfiguration",
        "description": "Improperly configured permissions, exposed files, and protocol-level misconfigurations.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Exposed Sensitive Files",
                "topic": "Git Exposure, Env File Leak, Debug Console",
                "cmd_code": "A05 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Path Traversal and LFI",
                "topic": "Path Traversal, LFI, PHP Wrappers, Arbitrary File Read",
                "cmd_code": "A05 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "HTTP Request Smuggling",
                "topic": "HTTP Request Smuggling, CL.TE, Response Queue Poisoning",
                "cmd_code": "A05 hard"
            }
        ]
    },
    {
        "id": "A06",
        "code": "A06:2025",
        "title": "Vulnerable & Outdated Components",
        "description": "Using software with known CVEs and outdated third-party libraries.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Known Component CVE",
                "topic": "Known CVE, Framework Auth Bypass, Header Injection",
                "cmd_code": "A06 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "XML External Entity (XXE)",
                "topic": "XXE, XML Parser, File Read, Internal SSRF",
                "cmd_code": "A06 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "JNDI / Log4Shell Injection",
                "topic": "Log4Shell, JNDI Lookup, Untrusted Logging, RCE",
                "cmd_code": "A06 hard"
            }
        ]
    },
    {
        "id": "A07",
        "code": "A07:2025",
        "title": "Identification & Authentication Failures",
        "description": "Failures in identity verification, session management, and authentication workflows.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Predictable Session Token",
                "topic": "Session Hijacking, Sequential Tokens, Weak Session ID",
                "cmd_code": "A07 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "OAuth 2.0 Flaws",
                "topic": "OAuth, Open Redirect, Authorization Code Interception",
                "cmd_code": "A07 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "MFA Bypass and Session Fixation",
                "topic": "MFA Bypass, Response Manipulation, Session Fixation",
                "cmd_code": "A07 hard"
            }
        ]
    },
    {
        "id": "A08",
        "code": "A08:2025",
        "title": "Software & Data Integrity Failures",
        "description": "Applications failing to verify integrity of uploads, templates, and serialized data objects.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "Malicious File Upload",
                "topic": "File Upload, Webshell, MIME Bypass, Double Extension",
                "cmd_code": "A08 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Server-Side Template Injection (SSTI)",
                "topic": "SSTI, Jinja2, Sandbox Escape, Secret Key Leak",
                "cmd_code": "A08 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Insecure Deserialization",
                "topic": "PHP Deserialization, POP Gadget Chain, Object Injection, RCE",
                "cmd_code": "A08 hard"
            }
        ]
    },
    {
        "id": "A09",
        "code": "A09:2025",
        "title": "Security Logging & Monitoring Failures",
        "description": "Insufficient logging and exploiting logging mechanisms as an attack vector.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "CRLF Log Injection",
                "topic": "CRLF Injection, Log Forgery, Audit Log Tampering",
                "cmd_code": "A09 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "Verbose Error Data Leak",
                "topic": "Error Handling, Stack Trace, Database Credentials Leak",
                "cmd_code": "A09 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "Blind XSS in Log Dashboard",
                "topic": "Blind XSS, Log Monitoring Panel, Admin Cookie Theft",
                "cmd_code": "A09 hard"
            }
        ]
    },
    {
        "id": "A10",
        "code": "A10:2025",
        "title": "Server-Side Request Forgery (SSRF) & API Security",
        "description": "Applications fetching remote resources without verifying destination targets.",
        "options": [
            {
                "level": "Option 1 (Easy)",
                "name": "SSRF Filter Bypass",
                "topic": "SSRF, Localhost Bypass, Alternative IP Formats",
                "cmd_code": "A10 easy"
            },
            {
                "level": "Option 2 (Medium)",
                "name": "SSRF Internal Pivot",
                "topic": "SSRF, Internal Subnet Port Scan, Private Admin API",
                "cmd_code": "A10 medium"
            },
            {
                "level": "Option 3 (Hard)",
                "name": "SSRF Cloud Metadata Exfiltration",
                "topic": "SSRF, AWS Metadata, 169.254.169.254, IAM Credentials, S3",
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
        launcher_script = os.path.join(app.root_path, "scripts", "start_challenge.sh")
        if os.path.exists(launcher_script):
            subprocess.run([launcher_script, category, level], check=True)
            return jsonify({
                "success": True, 
                "message": f"Lab {category} ({level}) started on port {6002 if category.lower() + '-' + level.lower() == 'a01-medium' else 6001}",
                "port": 6002 if category.lower() + '-' + level.lower() == 'a01-medium' else 6001,
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
