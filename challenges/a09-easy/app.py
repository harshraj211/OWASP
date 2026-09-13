import os
import time
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a09-easy"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

ACCOUNTS = {
    "sec_auditor": {
        "password": "Auditor2026!",
        "role": "Lead Compliance Auditor"
    }
}

SIEM_EVENTS = []
BLACKLISTED_IPS = set()
IP_FAILURES = {} # ip -> count

def log_siem_event(ip, endpoint, event_type, user, blocked=False):
    SIEM_EVENTS.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "endpoint": endpoint,
        "type": event_type,
        "user": user or "unknown",
        "blocked": blocked
    })

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html', blacklisted=list(BLACKLISTED_IPS))

@app.route('/compliance')
def compliance():
    return render_template('compliance.html')

@app.route('/siem/monitor')
def siem_monitor():
    return render_template('siem.html', events=SIEM_EVENTS[-25:])

@app.route('/api/v1/docs')
def api_docs():
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "Sentinel SOC Partner SSO & Ingestion Gateway",
            "version": "1.2.0"
        },
        "endpoints": {
            "/api/v1/sso/partner-auth": {
                "method": "POST",
                "summary": "Legacy partner single sign-on authentication service (bypasses centralized SIEM event streamer).",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Authentication successful"},
                    "401": {"description": "Invalid credentials"}
                }
            }
        }
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr or "127.0.0.1"
    if ip in BLACKLISTED_IPS:
        return render_template('login.html', error=f"Access Denied: IP {ip} is blacklisted by SIEM intrusion prevention."), 403

    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # Monitored login endpoint
    if username in ACCOUNTS and ACCOUNTS[username]["password"] == password:
        log_siem_event(ip, "/login", "AUTH_SUCCESS", username, blocked=False)
        IP_FAILURES[ip] = 0
        session['user'] = username
        session['role'] = ACCOUNTS[username]["role"]
        return redirect(url_for('vault'))
    else:
        IP_FAILURES[ip] = IP_FAILURES.get(ip, 0) + 1
        blocked = False
        if IP_FAILURES[ip] >= 3:
            BLACKLISTED_IPS.add(ip)
            blocked = True
        log_siem_event(ip, "/login", "AUTH_FAIL", username, blocked=blocked)
        if blocked:
            return render_template('login.html', error="Intrusion Detected: Your IP has been blacklisted by the SIEM automated sensor."), 403
        return render_template('login.html', error=f"Invalid credentials. Warning: {3 - IP_FAILURES[ip]} attempt(s) remaining before automatic IP blacklist."), 401

@app.route('/api/v1/sso/partner-auth', methods=['POST'])
def api_partner_auth():
    # VULNERABILITY: Missing Login Logs
    # Failed login attempts on this endpoint are completely omitted from SIEM_EVENTS,
    # and no IP blacklisting / rate-limiting is enforced!
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if username in ACCOUNTS and ACCOUNTS[username]["password"] == password:
        session['user'] = username
        session['role'] = ACCOUNTS[username]["role"]
        return jsonify({
            "success": True,
            "message": "Authenticated via Partner SSO",
            "role": ACCOUNTS[username]["role"],
            "redirect": "/auditor/vault"
        })
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/auditor/vault')
def vault():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('vault.html', flag=DYNAMIC_FLAG)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')


if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6025)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
