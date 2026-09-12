import os
import time
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a07-hard"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# Linear Congruential Generator Parameters (Numerical Recipes)
LCG_A = 1664525
LCG_C = 1013904223
LCG_M = 2**32

current_state = int(time.time() * 1000) % LCG_M

def generate_token():
    global current_state
    current_state = (LCG_A * current_state + LCG_C) % LCG_M
    return f"{current_state:08x}"

# User database
USERS = {
    "admin@apexbiologistics.net": {
        "password": secrets.token_hex(16),
        "role": "Chief Medical Director"
    },
    "researcher_demo@apexbiologistics.net": {
        "password": "Researcher2026!",
        "role": "Staff Investigator"
    }
}

ACTIVE_TOKENS = {} # email -> token
OUTBOX = []        # list of {time, recipient, subject, token}

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trials')
def trials():
    return render_template('trials.html')

@app.route('/outbox')
def outbox_view():
    return render_template('outbox.html', outbox=OUTBOX[-20:])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()

    user = USERS.get(email)
    if not user or user['password'] != password:
        return render_template('login.html', error="Invalid email address or clinical password."), 401
    
    session['user'] = email
    session['role'] = user['role']
    if user['role'] == "Chief Medical Director":
        return redirect(url_for('governance'))
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    email = request.form.get('email', '').strip().lower()
    if email not in USERS:
        return render_template('forgot_password.html', message="If that email is registered, a token has been dispatched.")
    
    token = generate_token()
    ACTIVE_TOKENS[email] = token

    # Only non-admin emails appear in public relay outbox
    if "admin" not in email:
        OUTBOX.append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "recipient": email,
            "subject": "Password Recovery Request",
            "token": token
        })
    
    return render_template('forgot_password.html', message=f"Password recovery token dispatched for {email}. Please inspect your delivery inbox.")

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset_password.html')
    
    email = request.form.get('email', '').strip().lower()
    token = request.form.get('token', '').strip().lower()
    new_password = request.form.get('new_password', '').strip()

    if not email or not token or not new_password:
        return render_template('reset_password.html', error="All fields are required."), 400
    
    expected_token = ACTIVE_TOKENS.get(email)
    if not expected_token or expected_token.lower() != token:
        return render_template('reset_password.html', error="Invalid or expired recovery token."), 403
    
    USERS[email]['password'] = new_password
    ACTIVE_TOKENS.pop(email, None)
    return render_template('login.html', message="Password successfully reset. You may now sign in.")

@app.route('/admin/governance')
def governance():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('role') != "Chief Medical Director":
        return "Access Denied: Unrestricted Governance authority required.", 403
    return render_template('governance.html', flag=DYNAMIC_FLAG)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6021)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
