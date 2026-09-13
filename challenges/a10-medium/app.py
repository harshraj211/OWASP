import os
import time
import json
import math
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

# Redundant Consensus Node Registry
# Three distributed telemetry ingestion nodes
NODES = {
    "alpha": {
        "name": "Node-Alpha (500kV Main Bus)",
        "fault_until": 0,
        "last_fault": None
    },
    "beta": {
        "name": "Node-Beta (230kV Thermal Feeder)",
        "fault_until": 0,
        "last_fault": None
    },
    "gamma": {
        "name": "Node-Gamma (Tie-Line Intertie)",
        "fault_until": 0,
        "last_fault": None
    }
}

WATCHDOG_TIMEOUT = 20  # 20 seconds before faulted node recovers

def get_node_states():
    now = time.time()
    states = {}
    for k, v in NODES.items():
        is_faulted = now < v["fault_until"]
        states[k] = {
            "name": v["name"],
            "status": "FAULT" if is_faulted else "HEALTHY",
            "is_faulted": is_faulted,
            "seconds_remaining": max(0, int(v["fault_until"] - now)) if is_faulted else 0,
            "last_fault": v["last_fault"] if is_faulted else None
        }
    return states

def evaluate_consensus():
    states = get_node_states()
    healthy_count = sum(1 for s in states.values() if s["status"] == "HEALTHY")
    # Quorum requires at least 2 of 3 healthy nodes
    has_quorum = healthy_count >= 2
    return has_quorum, healthy_count, states

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    has_quorum, healthy_count, states = evaluate_consensus()
    return render_template('index.html', has_quorum=has_quorum, healthy_count=healthy_count, nodes=states)

@app.route('/substations')
def substations():
    return render_template('substations.html')

@app.route('/system/safety-interlock')
def interlock_status():
    has_quorum, healthy_count, states = evaluate_consensus()
    return render_template('status.html', has_quorum=has_quorum, healthy_count=healthy_count, nodes=states)

@app.route('/grid/telemetry', methods=['GET', 'POST'])
@app.route('/api/v1/telemetry/submit', methods=['POST'])
def telemetry_view():
    msg = None
    fault = None
    target_node = "alpha"

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        if not data and request.form:
            raw_payload = request.form.get('payload', '')
            try:
                data = json.loads(raw_payload)
            except Exception as je:
                msg = f"Malformed JSON Payload: {str(je)}"
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({"status": "error", "error": msg}), 400
                return render_template('telemetry.html', message=msg, fault_message=None, nodes=get_node_states())

        target_node = str(data.get("node", "alpha")).lower().strip()
        if target_node not in NODES:
            target_node = "alpha"

        # Stage 1: Ingestion Schema Validation
        try:
            v_kv = float(data.get("voltage_kv", 500.0))
            i_a = float(data.get("current_a", 1200.0))
            p_mw = float(data.get("active_power_mw", 100.0))
            q_mvar = float(data.get("reactive_power_mvar", 20.0))
        except (ValueError, TypeError) as val_err:
            msg = f"Stage 1 Ingestion Validation Failed: telemetry parameters must be valid numeric values ({str(val_err)})."
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"status": "error", "stage": "ingestion_validation", "error": msg}), 400
            return render_template('telemetry.html', message=msg, fault_message=None, nodes=get_node_states())

        # Stage 2: Physics Stability Calculation Engine
        try:
            discriminant = (v_kv ** 2) - (q_mvar * 25.0)
            if discriminant < 0:
                raise ValueError(f"Negative radical in stability matrix: {discriminant:.2f} < 0")
            
            sil_margin = math.sqrt(discriminant) / p_mw
            msg = f"Telemetry frame committed for {NODES[target_node]['name']}. SIL Margin: {sil_margin:.4f}. Phase Lock: OK."
            
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    "status": "success",
                    "node": target_node,
                    "sil_margin": round(sil_margin, 4),
                    "phase_lock": True
                }), 200

        except Exception as crash_exc:
            # Unhandled Exception in Node Physics Engine
            NODES[target_node]["fault_until"] = time.time() + WATCHDOG_TIMEOUT
            NODES[target_node]["last_fault"] = f"{type(crash_exc).__name__}: {str(crash_exc)}"
            fault = f"CRITICAL DAEMON FAULT on {NODES[target_node]['name']}: {type(crash_exc).__name__} ({str(crash_exc)}). Worker Thread Quarantined."
            
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    "status": "error",
                    "stage": "physics_calculation",
                    "node": target_node,
                    "error": type(crash_exc).__name__,
                    "detail": str(crash_exc),
                    "node_state": "FAULT"
                }), 500

    return render_template('telemetry.html', message=msg, fault_message=fault, nodes=get_node_states())

@app.route('/core/override')
@app.route('/api/v1/core/override', methods=['GET', 'POST'])
def core_override():
    has_quorum, healthy_count, states = evaluate_consensus()
    
    if has_quorum:
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "status": "denied",
                "error": "QuorumActive",
                "message": f"Access Denied: Safety consensus active ({healthy_count}/3 nodes online). Interlocks locked."
            }), 403
        return render_template('override.html', has_quorum=True, healthy_count=healthy_count, nodes=states, flag=None), 403

    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            "status": "authorized",
            "message": "Emergency Grid Preservation Activated: Quorum collapsed, interlocks disengaged.",
            "flag": DYNAMIC_FLAG
        }), 200

    return render_template('override.html', has_quorum=False, healthy_count=healthy_count, nodes=states, flag=DYNAMIC_FLAG)

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6029)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
