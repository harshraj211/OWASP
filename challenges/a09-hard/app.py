import os
import time
import hashlib
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a09-hard"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

ADMIN_KEY = "cert_titan_secops_7719"

def compute_hash(index, prev_hash, timestamp, event_type, details):
    content = f"{index}|{prev_hash}|{timestamp}|{event_type}|{details}".encode('utf-8')
    return hashlib.sha256(content).hexdigest()

# Initial Genesis Ledger
LEDGER = [
    {
        "index": 0,
        "timestamp": "2026-09-01 00:00:00",
        "event_type": "GENESIS_BLOCK",
        "details": "Titan Cryptographic Ledger Initialized",
        "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "hash": ""
    },
    {
        "index": 1,
        "timestamp": "2026-09-01 00:01:00",
        "event_type": "SYSTEM_BOOT",
        "details": "Command Center Core Services Activated (Maintenance Certificate: cert_titan_secops_7719)",
        "prev_hash": "",
        "hash": ""
    },
    {
        "index": 2,
        "timestamp": "2026-09-01 00:05:00",
        "event_type": "UNAUTHORIZED_BREACH_DETECTED",
        "details": "Perimeter intrusion detected at classified vault sector 4; lockdown initiated",
        "prev_hash": "",
        "hash": ""
    },
    {
        "index": 3,
        "timestamp": "2026-09-01 00:08:00",
        "event_type": "TELEMETRY_HEARTBEAT",
        "details": "Automated perimeter telemetry heartbeat verified",
        "prev_hash": "",
        "hash": ""
    },
    {
        "index": 4,
        "timestamp": "2026-09-01 00:15:00",
        "event_type": "TELEMETRY_HEARTBEAT",
        "details": "Sector 9 routine system telemetry verified",
        "prev_hash": "",
        "hash": ""
    }
]

# Calculate initial hashes
LEDGER[0]["hash"] = compute_hash(0, LEDGER[0]["prev_hash"], LEDGER[0]["timestamp"], LEDGER[0]["event_type"], LEDGER[0]["details"])
for i in range(1, len(LEDGER)):
    LEDGER[i]["prev_hash"] = LEDGER[i - 1]["hash"]
    LEDGER[i]["hash"] = compute_hash(i, LEDGER[i]["prev_hash"], LEDGER[i]["timestamp"], LEDGER[i]["event_type"], LEDGER[i]["details"])

def append_block(event_type, details):
    prev = LEDGER[-1]
    idx = len(LEDGER)
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    h = compute_hash(idx, prev["hash"], ts, event_type, details)
    LEDGER.append({
        "index": idx,
        "timestamp": ts,
        "event_type": event_type,
        "details": details,
        "prev_hash": prev["hash"],
        "hash": h
    })

def validate_ledger():
    """Validates the chain integrity and checks for breach entries."""
    has_breach = False
    chain_valid = True
    reason = None

    for i in range(len(LEDGER)):
        b = LEDGER[i]
        if "BREACH" in b["event_type"]:
            has_breach = True
            if not reason:
                reason = f"Security Violation in Block #{b['index']}: {b['event_type']}"

        if i > 0:
            prev = LEDGER[i - 1]
            if b["prev_hash"] != prev["hash"]:
                chain_valid = False
                if not reason:
                    reason = f"Hash Chain broken at Block #{b['index']}: prev_hash mismatch"

        expected_hash = compute_hash(b["index"], b["prev_hash"], b["timestamp"], b["event_type"], b["details"])
        if b["hash"] != expected_hash:
            chain_valid = False
            if not reason:
                reason = f"Hash Chain broken at Block #{b['index']}: hash recalculation mismatch"

    return has_breach, chain_valid, reason

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    has_breach, chain_valid, _ = validate_ledger()
    return render_template('index.html', ledger=LEDGER, has_breach=has_breach, chain_valid=chain_valid)

@app.route('/clearance', methods=['GET', 'POST'])
def clearance():
    msg = None
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        session['user'] = u
        append_block("BADGE_ENROLLED", f"Operator call-sign registered: {u}")
        msg = f"Badge session established for call-sign: {u}"
    return render_template('clearance.html', message=msg)

@app.route('/robots.txt')
def robots_txt():
    return "User-agent: *\nDisallow: /audit/console\nDisallow: /vault/classified\nDisallow: /api/v1/audit/\n", 200, {'Content-Type': 'text/plain'}

@app.route('/audit/ledger')
def ledger_view():
    _, chain_valid, _ = validate_ledger()
    return render_template('ledger.html', ledger=LEDGER, chain_valid=chain_valid)

@app.route('/api/v1/audit/ledger')
def api_ledger():
    _, chain_valid, reason = validate_ledger()
    return jsonify({"ledger": LEDGER, "chain_valid": chain_valid, "reason": reason})

@app.route('/audit/console')
def console_view():
    msg = session.pop('console_msg', None)
    err = session.pop('console_err', None)
    return render_template('console.html', message=msg, error=err)

@app.route('/vault/classified')
def classified_vault():
    auth_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
    if auth_key == ADMIN_KEY:
        session['maintenance_authorized'] = True

    # If not authorized by maintenance or officer clearance, trigger breach detection and log it!
    if not session.get('maintenance_authorized') and session.get('user') != 'titan_authorized_officer':
        caller = session.get('user') or 'anonymous_intruder'
        append_block("UNAUTHORIZED_BREACH_DETECTED", f"Intrusion alarm triggered by {caller} at classified vault.")

    has_breach, chain_valid, reason = validate_ledger()
    access_granted = (not has_breach) and chain_valid
    return render_template('classified.html', access_granted=access_granted, failure_reason=reason, flag=DYNAMIC_FLAG)

@app.route('/api/v1/audit/tamper-block', methods=['POST'])
def tamper_block():
    data = request.get_json(silent=True) or request.form
    key = data.get('admin_key', '').strip()
    if key != ADMIN_KEY:
        if request.is_json:
            return jsonify({"success": False, "error": "Unauthorized: Invalid SecOps Admin Key."}), 403
        session['console_err'] = "Unauthorized: Invalid SecOps Admin Key."
        return redirect(url_for('console_view'))

    try:
        idx = int(data.get('index', -1))
    except (ValueError, TypeError):
        idx = -1

    if not (0 <= idx < len(LEDGER)):
        if request.is_json:
            return jsonify({"success": False, "error": "Invalid block index."}), 400
        session['console_err'] = "Invalid block index."
        return redirect(url_for('console_view'))

    new_type = data.get('event_type')
    new_details = data.get('details')
    new_prev = data.get('prev_hash')
    new_hash = data.get('hash')
    new_ts = data.get('timestamp')

    if new_type is not None:
        LEDGER[idx]["event_type"] = str(new_type)
    if new_details is not None:
        LEDGER[idx]["details"] = str(new_details)
    if new_prev is not None:
        LEDGER[idx]["prev_hash"] = str(new_prev)
    if new_hash is not None:
        LEDGER[idx]["hash"] = str(new_hash)
    if new_ts is not None:
        LEDGER[idx]["timestamp"] = str(new_ts)

    session['maintenance_authorized'] = True
    msg = f"Block #{idx} updated in ledger."
    if request.is_json:
        has_breach, chain_valid, reason = validate_ledger()
        return jsonify({
            "success": True,
            "message": msg,
            "block": LEDGER[idx],
            "chain_valid": chain_valid,
            "has_breach": has_breach
        })
    session['console_msg'] = msg
    return redirect(url_for('console_view'))


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
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6027)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
