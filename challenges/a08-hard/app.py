import os
import io
import base64
import pickle
import secrets
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a08-hard"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Write flag to /flag.txt if possible, and local flag.txt
for path in ["/flag.txt", os.path.join(BASE_DIR, "flag.txt")]:
    try:
        with open(path, "w") as f:
            f.write(DYNAMIC_FLAG)
    except Exception:
        pass

class DataPipeline:
    def __init__(self, name, stages):
        self.name = name
        self.stages = stages
    def evaluate(self):
        return f"Pipeline '{self.name}' evaluated across {len(self.stages)} stages: Status 100% Complete."

class RestrictedUnpickler(pickle.Unpickler):
    BLOCKED_MODULES = {'os', 'subprocess', 'posix', 'sys', 'commands'}

    def find_class(self, module, name):
        if module in self.BLOCKED_MODULES:
            raise pickle.UnpicklingError(f"Security Sandbox Violation: Module '{module}' is blacklisted.")
        return super().find_class(module, name)

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datasets')
def datasets():
    return render_template('datasets.html')

@app.route('/pipeline')
def pipeline_view():
    return render_template('pipeline.html')

@app.route('/pipeline/export')
def pipeline_export():
    p = DataPipeline("Standard-AeroTelemetry-Aggregator", [
        "Filter(altitude > 30000)",
        "Map(speed_mach)",
        "Reduce(mean)"
    ])
    raw = pickle.dumps(p)
    b64 = base64.b64encode(raw).decode('utf-8')
    return jsonify({
        "pipeline_name": p.name,
        "format": "pickle_base64",
        "token": b64
    })

@app.route('/pipeline/import', methods=['GET', 'POST'])
def pipeline_import():
    if request.method == 'GET':
        return render_template('import.html')
    
    payload = request.form.get('payload', '').strip()
    if not payload:
        return render_template('import.html', error="Serialized payload is required."), 400
    
    try:
        raw_bytes = base64.b64decode(payload)
        unpickler = RestrictedUnpickler(io.BytesIO(raw_bytes))
        obj = unpickler.load()

        if hasattr(obj, 'evaluate') and callable(obj.evaluate):
            result = obj.evaluate()
        else:
            result = f"Deserialized object of type: {type(obj).__name__}\nValue: {str(obj)}"
        return render_template('import.html', result=result)
    except Exception as e:
        return render_template('import.html', error=f"Deserialization Exception: {str(e)}"), 500

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6024)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
