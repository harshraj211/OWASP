import os
import time
import json
import secrets
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a10-medium"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# Fail-Open state timestamp
FAIL_OPEN_UNTIL = 0

def is_fail_open_active():
    return time.time() < FAIL_OPEN_UNTIL

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html', is_fail_open=is_fail_open_active())

@app.route('/substations')
def substations():
    return render_template('substations.html')

@app.route('/system/safety-interlock')
def interlock_status():
    return render_template('status.html', is_fail_open=is_fail_open_active())

@app.route('/grid/telemetry', methods=['GET', 'POST'])
def telemetry_view():
    global FAIL_OPEN_UNTIL
    msg = None
    fault = None

    if request.method == 'POST':
        raw_data = request.form.get('payload') or request.get_data(as_text=True)
        try:
            data = json.loads(raw_data)
            harmonics = data.get('harmonics')
            
            # VULNERABILITY: Unhandled Exception in Safety Daemon Logic
            # The calculation expects a list of numeric floats. Supplying non-numeric elements,
            # strings, or None causes an unhandled TypeError / ValueError which crashes the daemon
            # into a 60-second fail-open emergency bypass state!
            thd = sum([h ** 2 for h in harmonics]) ** 0.5
            msg = f"Telemetry frame processed successfully. THD Index: {thd:.4f}. Interlocks Nominal."
        except json.JSONDecodeError as je:
            msg = f"Invalid JSON Syntax: {str(je)}"
        except Exception as e:
            FAIL_OPEN_UNTIL = time.time() + 60
            fault = f"CRITICAL FAULT: {type(e).__name__} in Telemetry Ingest Engine ({str(e)}). Safety Interlock Supervisor Crashed."
    
    return render_template('telemetry.html', message=msg, fault_message=fault)

@app.route('/core/override')
def core_override():
    return render_template('override.html', is_fail_open=is_fail_open_active(), flag=DYNAMIC_FLAG)

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6029)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
