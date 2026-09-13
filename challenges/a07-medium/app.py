import os
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a07-medium"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# Registered accounts
USERS = {
    "sysadmin_root": {
        "password": "AutumnSettlement#99",
        "role": "System Administrator",
        "mfa_enabled": True
    },
    "trader_bob": {
        "password": "TraderPassword123!",
        "role": "Liquidity Analyst",
        "mfa_enabled": False
    }
}

# The true secret TOTP key for root is never disclosed
ROOT_TOTP_SECRET = secrets.token_hex(16)

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = USERS.get(username)
    if not user or user["password"] != password:
        return render_template('login.html', error="Invalid username or password."), 401

    session['user'] = username
    session['role'] = user['role']

    if user['mfa_enabled']:
        session['mfa_required'] = True
        session['mfa_verified'] = False
        return redirect(url_for('mfa_view'))
    else:
        session['mfa_required'] = False
        session['mfa_verified'] = True
        return redirect(url_for('dashboard'))

@app.route('/auth/2fa', methods=['GET', 'POST'])
def mfa_view():
    if not session.get('user'):
        return redirect(url_for('login'))
    if not session.get('mfa_required') or session.get('mfa_verified'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('mfa.html')
    
    code = request.form.get('code', '').strip()
    return render_template('mfa.html', error="Invalid TOTP authentication code. Attempt logged to SecOps monitor."), 403

@app.route('/api/v1/auth/verify-backup', methods=['POST'])
def api_verify_backup():
    """Verify an emergency backup code to satisfy MFA step-up."""
    if not session.get('user'):
        return jsonify({"success": False, "error": "No active primary session."}), 401

    data = request.get_json(silent=True) or {}
    submitted_code = data.get('backup_code')

    user_record = USERS.get(session.get('user'), {})
    expected_code = user_record.get('backup_code')

    # Flaw: Uninitialized database field returns None. Submitting {"backup_code": null} results in None == None (True).
    if submitted_code == expected_code:
        session['mfa_verified'] = True
        return jsonify({
            "success": True,
            "message": "Emergency backup verification successful. Session elevated.",
            "redirect": "/dashboard"
        }), 200

    return jsonify({
        "success": False,
        "error": "Invalid emergency backup recovery code."
    }), 403

# Keep legacy route alias for compatibility
@app.route('/api/v1/auth/session/emergency-dispatch', methods=['POST'])
def api_emergency_dispatch():
    return api_verify_backup()

@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('mfa_required') and not session.get('mfa_verified'):
        return redirect(url_for('mfa_view'))
    return render_template('dashboard.html')

@app.route('/security/audit-vault')
def audit_vault():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('mfa_required') and not session.get('mfa_verified'):
        return redirect(url_for('mfa_view'))
    if session.get('role') != 'System Administrator':
        return "Forbidden: Administrator role required.", 403
    return render_template('audit_vault.html', flag=DYNAMIC_FLAG)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')


if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6020)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
