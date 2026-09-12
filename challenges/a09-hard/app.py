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

ADMIN_KEY = "TITAN_SEC_MAINT_2026"

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
        "details": "Command Center Core Services Activated",
        "prev_hash": "",
        "hash": ""
    }
]

# Calculate initial hashes
LEDGER[0]["hash"] = compute_hash(0, LEDGER[0]["prev_hash"], LEDGER[0]["timestamp"], LEDGER[0]["event_type"], LEDGER[0]["details"])
LEDGER[1]["prev_hash"] = LEDGER[0]["hash"]
LEDGER[1]["hash"] = compute_hash(1, LEDGER[1]["prev_hash"], LEDGER[1]["timestamp"], LEDGER[1]["event_type"], LEDGER[1]["details"])

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

@app.route('/audit/ledger')
def ledger_view():
    _, chain_valid, _ = validate_ledger()
    return render_template('ledger.html', ledger=LEDGER, chain_valid=chain_valid)

@app.route('/audit/console')
def console_view():
    msg = session.pop('console_msg', None)
    err = session.pop('console_err', None)
    return render_template('console.html', message=msg, error=err)

@app.route('/vault/classified')
def classified_vault():
    # If not authorized by maintenance or officer clearance, trigger breach detection and log it!
    if not session.get('maintenance_authorized') and session.get('user') != 'titan_authorized_officer':
        caller = session.get('user') or 'anonymous_intruder'
        append_block("UNAUTHORIZED_BREACH_DETECTED", f"Intrusion alarm triggered by {caller} at classified vault.")

    has_breach, chain_valid, reason = validate_ledger()
    access_granted = (not has_breach) and chain_valid
    return render_template('classified.html', access_granted=access_granted, failure_reason=reason, flag=DYNAMIC_FLAG)

@app.route('/api/v1/audit/tamper-block', methods=['POST'])
def tamper_block():
    key = request.form.get('admin_key') or (request.get_json(silent=True) or {}).get('admin_key')
    if key != ADMIN_KEY:
        session['console_err'] = "Unauthorized: Invalid SecOps Admin Key."
        return redirect(url_for('console_view'))

    idx = int(request.form.get('index') or (request.get_json(silent=True) or {}).get('index', -1))
    new_type = request.form.get('event_type') or (request.get_json(silent=True) or {}).get('event_type')
    new_details = request.form.get('details') or (request.get_json(silent=True) or {}).get('details')

    if 0 <= idx < len(LEDGER):
        LEDGER[idx]["event_type"] = new_type
        LEDGER[idx]["details"] = new_details
        session['maintenance_authorized'] = True
        session['console_msg'] = f"Block #{idx} updated. Remember to recompute ledger hash chain."
        return redirect(url_for('console_view'))
    
    session['console_err'] = "Invalid block index."
    return redirect(url_for('console_view'))

@app.route('/api/v1/audit/recompute-chain', methods=['POST'])
def recompute_chain():
    key = request.form.get('admin_key') or (request.get_json(silent=True) or {}).get('admin_key')
    if key != ADMIN_KEY:
        session['console_err'] = "Unauthorized: Invalid SecOps Admin Key."
        return redirect(url_for('console_view'))

    # Rebuild chain from Genesis
    for i in range(len(LEDGER)):
        if i == 0:
            LEDGER[0]["hash"] = compute_hash(0, LEDGER[0]["prev_hash"], LEDGER[0]["timestamp"], LEDGER[0]["event_type"], LEDGER[0]["details"])
        else:
            LEDGER[i]["prev_hash"] = LEDGER[i - 1]["hash"]
            LEDGER[i]["hash"] = compute_hash(i, LEDGER[i]["prev_hash"], LEDGER[i]["timestamp"], LEDGER[i]["event_type"], LEDGER[i]["details"])

    session['maintenance_authorized'] = True
    session['console_msg'] = "Cryptographic ledger hash chain successfully recomputed and verified."
    return redirect(url_for('console_view'))

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6027)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
