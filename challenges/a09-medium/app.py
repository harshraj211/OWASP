import os
import re
import time
import hashlib
import secrets
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a09-medium"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_LOG = os.path.join(BASE_DIR, "audit.log")

# Seed the initial audit log if empty
if not os.path.exists(AUDIT_LOG):
    with open(AUDIT_LOG, "w") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SYSTEM] Apex Commercial Banking Audit Daemon Initialized.\n")
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Compliance Rule 44.B Active.\n")

def get_daily_token():
    return hashlib.md5(f"APEX_AUDIT_{time.strftime('%Y%m%d')}".encode('utf-8')).hexdigest()

def is_override_active():
    """Scans audit.log for injected or certified AUDIT_OVERRIDE entries."""
    if not os.path.exists(AUDIT_LOG):
        return False
    
    expected = get_daily_token()
    pattern = re.compile(r"\[[0-9: -]+\]\s+\[AUDIT_OVERRIDE\]\s+CLEARANCE_TOKEN=([0-9a-fA-F]{32})\s+STATUS=CERTIFIED")
    try:
        with open(AUDIT_LOG, "r", errors="ignore") as f:
            for line in f:
                m = pattern.search(line)
                if m and m.group(1).lower() == expected.lower():
                    return True
    except Exception:
        pass
    return False

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html', override_active=is_override_active())

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    msg = None
    if request.method == 'POST':
        beneficiary = request.form.get('beneficiary', '').strip()
        amount = request.form.get('amount', '0').strip()
        memo = request.form.get('memo', '') # Raw memo with CRLF preserved!

        tx_id = f"TX-{secrets.token_hex(4).upper()}"
        ts = time.strftime('%Y-%m-%d %H:%M:%S')

        # VULNERABILITY: Log Injection (CRLF)
        # User input 'memo' is concatenated directly into audit.log without removing newlines
        log_entry = f"[{ts}] [TRANSACTION] TX_ID={tx_id} AMOUNT={amount} BEN={beneficiary} MEMO={memo}\n"
        with open(AUDIT_LOG, "a") as f:
            f.write(log_entry)

        msg = f"Wire Transfer {tx_id} submitted and appended to compliance audit stream."
    return render_template('transfer.html', message=msg)

@app.route('/compliance/stream')
def stream_view():
    lines = []
    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r", errors="ignore") as f:
            lines = [l.strip() for l in f.readlines()]
    return render_template('stream.html', log_lines=lines[-50:])

@app.route('/robots.txt')
def robots_txt():
    return "User-agent: *\nDisallow: /vault/treasury\nDisallow: /compliance/status\n", 200, {'Content-Type': 'text/plain'}

@app.route('/compliance/status')
def status_view():
    return render_template('status.html', 
                           override_active=is_override_active())

@app.route('/vault/treasury')
def treasury_vault():
    return render_template('vault.html', 
                           override_active=is_override_active(), 
                           flag=DYNAMIC_FLAG)


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
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6026)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
