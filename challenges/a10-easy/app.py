import os
import time
import secrets
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a10-easy"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# 32-character master key partitioned into four 8-byte chunks
# Chunk 0 (+0x00): QE_KEY{9
# Chunk 1 (+0x08): f81_b3c4
# Chunk 2 (+0x10): _771a_d9
# Chunk 3 (+0x18): 01_f5c2}
INTERNAL_VAULT_TOKEN = "QE_KEY{9f81_b3c4_771a_d901_f5c2}"

class SharedWorkerState:
    """Simulates an unsynchronized shared memory partition in the worker thread."""
    active_slice_ref = None

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/api-spec')
def api_spec():
    return render_template('api.html')

@app.route('/portfolio', methods=['GET', 'POST'])
@app.route('/api/v1/matrix/optimize', methods=['POST'])
def portfolio():
    err_trace = None
    res = None
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        if not data and request.form:
            data = {
                "assets": request.form.get('assets', 'AAPL, NVDA'),
                "weights": request.form.get('weights', '0.5, 0.5'),
                "covariance_factor": request.form.get('covariance_factor', '1.0'),
                "matrix_config": {
                    "algorithm": request.form.get('algorithm', 'cholesky_decomposition'),
                    "worker_slice_ref": request.form.get('worker_slice_ref', '0x00'),
                    "thread_affinity": "balanced"
                }
            }

        matrix_cfg = data.get("matrix_config", {})
        if not isinstance(matrix_cfg, dict):
            matrix_cfg = {}
        
        slice_ref = str(matrix_cfg.get("worker_slice_ref", "0x00")).strip()
        cov_factor = data.get('covariance_factor', 1.0)
        
        # Concurrency race condition trigger
        # Write incoming slice_ref into unsynchronized shared thread buffer
        SharedWorkerState.active_slice_ref = slice_ref
        
        # Artificial computation window (35ms) to enable simultaneous request collisions
        time.sleep(0.035)
        
        # Check if another concurrent request overwrote the active partition
        if SharedWorkerState.active_slice_ref != slice_ref:
            conflicting_slice = SharedWorkerState.active_slice_ref
            
            # Parse memory offset from slice_ref (supports 0x00, 0x08, 0x10, 0x18 or integer indexes)
            try:
                if slice_ref.lower().startswith('0x'):
                    offset = int(slice_ref, 16)
                else:
                    offset = int(slice_ref)
            except Exception:
                offset = 0
                
            # Align to 8-byte boundaries within the 32-byte secret
            chunk_offset = (offset // 8 * 8) % 32
            chunk_slice = INTERNAL_VAULT_TOKEN[chunk_offset:chunk_offset + 8]
            hex_bytes = " ".join(f"{b:02x}" for b in chunk_slice.encode())
            
            err_trace = (
                f"Traceback (most recent call last):\n"
                f"  File \"/app/core_engine/matrix_worker.py\", line 148, in execute_partition\n"
                f"    raise WorkerMemoryCollisionException(f\"Dirty read collision: worker_slice_ref [{slice_ref}] overwritten by [{conflicting_slice}]\")\n"
                f"WorkerMemoryCollisionException: Dirty read collision: worker_slice_ref [{slice_ref}] overwritten by [{conflicting_slice}]\n\n"
                f"--- Unhandled Thread Frame Register Slice [Offset +0x{chunk_offset:02x}, Len 8 bytes] ---\n"
                f"{chunk_offset:08x}:  {hex_bytes.ljust(24)}  |{chunk_slice}|\n"
                f"INTERNAL_ENDPOINT: /api/v1/internal/confidential-vault\n"
                f"FILESYSTEM_PATH: /app/core_engine/secrets_vault.py\n"
            )
            
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    "status": "error",
                    "error": "WorkerMemoryCollisionException",
                    "collision_detected": True,
                    "worker_slice_ref": slice_ref,
                    "conflicting_slice_ref": conflicting_slice,
                    "stack_trace": err_trace
                }), 500
            return render_template('portfolio.html', error_trace=err_trace, calculation_result=None), 500
        
        # If no race condition occurred, computation completes normally
        try:
            factor = float(cov_factor)
            normalized_vol = (0.24 * 0.24) * factor
            res = f"Matrix Decomposed Successfully. Volatility: {normalized_vol:.4f} | Sharpe Ratio: 2.14 | Partition: {slice_ref}"
        except Exception:
            res = "Matrix Decomposed Successfully. Sharpe Ratio: 2.14"

        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "status": "success",
                "metrics": {
                    "sharpe_ratio": 2.14,
                    "volatility": 0.0576,
                    "slice_ref": slice_ref
                }
            }), 200

    return render_template('portfolio.html', error_trace=err_trace, calculation_result=res)

@app.route('/vault')
def vault_view():
    return render_template('vault.html', flag=None)

@app.route('/api/v1/internal/confidential-vault')
def internal_vault():
    token = request.args.get('token', '').strip()
    if token and token == INTERNAL_VAULT_TOKEN:
        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({"success": True, "flag": DYNAMIC_FLAG})
        return render_template('vault.html', flag=DYNAMIC_FLAG)
    return jsonify({"success": False, "error": "Unauthorized: Invalid internal vault token."}), 403


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
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6028)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    # threaded=True is required for concurrent request handling in dev server
    app.run(host='0.0.0.0', port=port, threaded=True)
