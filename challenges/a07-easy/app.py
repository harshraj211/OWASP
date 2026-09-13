import os
import secrets
import time
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a07-easy"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# Crew Directory
STAFF = [
    {"id": "EMP-1044", "name": "James Morrison", "username": "j.morrison", "hub": "JFK", "role": "Senior Captain (B787)", "joined": "Spring 2019"},
    {"id": "EMP-2088", "name": "Elena Rostova", "username": "e.rostova", "hub": "SFO", "role": "First Officer (A321)", "joined": "Spring 2024"},
    {"id": "EMP-3412", "name": "Sarah Jenkins", "username": "s.jenkins", "hub": "ORD", "role": "Station Operations Lead", "joined": "Summer 2021"},
    {"id": "EMP-4901", "name": "Marcus Vance", "username": "m.vance", "hub": "LAX", "role": "Chief Flight Dispatcher", "joined": "Fall 2023"},
    {"id": "EMP-5190", "name": "David Thorne", "username": "d.thorne", "hub": "DFW", "role": "Avionics Maintenance Tech", "joined": "Winter 2022"}
]

# Credentials: Marcus Vance still has default grandfathered password matching company memo formula
CREDENTIALS = {
    "m.vance": "LAX!Fall2023",
    "j.morrison": secrets.token_hex(18), # Complex rotated password
    "e.rostova": secrets.token_hex(18),
    "s.jenkins": secrets.token_hex(18),
    "d.thorne": secrets.token_hex(18)
}

FAILED_ATTEMPTS = {} # username -> {"count": int, "lock_until": float}

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crew-roster')
def roster():
    return render_template('roster.html', staff=STAFF)

@app.route('/bulletins')
def bulletins():
    return render_template('bulletins.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    now = time.time()

    # Check lock
    lock_info = FAILED_ATTEMPTS.get(username, {"count": 0, "lock_until": 0})
    if lock_info["lock_until"] > now:
        remaining = int(lock_info["lock_until"] - now)
        return render_template('login.html', error=f"Account locked due to consecutive failed attempts. Retry in {remaining}s."), 429

    if username in CREDENTIALS and CREDENTIALS[username] == password:
        # Success
        FAILED_ATTEMPTS.pop(username, None)
        session['user'] = username
        session['role'] = "Chief Flight Dispatcher" if username == "m.vance" else "Flight Crew"
        return redirect(url_for('dispatch'))
    else:
        # Failure
        lock_info["count"] += 1
        if lock_info["count"] >= 5:
            lock_info["lock_until"] = now + 120 # 2 minute lock
            FAILED_ATTEMPTS[username] = lock_info
            return render_template('login.html', error="Account locked: Exceeded 5 consecutive failed attempts."), 429
        else:
            FAILED_ATTEMPTS[username] = lock_info
            return render_template('login.html', error=f"Invalid credentials. Warning: {5 - lock_info['count']} attempt(s) remaining before lockout."), 401

@app.route('/dispatch/operations')
def dispatch():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('dispatch.html')

@app.route('/dispatch/manifest/classified')
def classified_manifest():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user') != 'm.vance':
        return "Access Denied: Chief Flight Dispatcher clearance required.", 403
    return render_template('manifest.html', flag=DYNAMIC_FLAG)

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
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6019)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
