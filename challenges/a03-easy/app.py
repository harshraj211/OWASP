"""A03 Easy: Software Supply Chain Failures - Known Component CVE & SBOM Dependency Audit.

Vulnerability:
The AeroGrid Avionics Telemetry Gateway ingests and processes flight telemetry manifests
formatted in YAML. The system depends on an outdated, vulnerable parser component:
PyYAML 5.3.1 (CVE-2020-14343).
An attacker inspecting the Software Bill of Materials (SBOM) at /api/v1/sbom can discover
the vulnerable transitive component and supply a weaponized YAML payload using
!!python/object/apply tags to execute code and retrieve the dynamic flag.
"""

import os
import secrets
import yaml
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a03-easy"
PORT = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6007)

def get_flag():
    env_flag = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if env_flag:
        return env_flag.strip()
    if os.path.exists("/flag.txt"):
        try:
            with open("/flag.txt", "r") as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

# Ensure flag is accessible via multiple standard locations
for flag_path in [
    "/flag.txt",
    "/tmp/flag.txt",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag.txt"),
]:
    try:
        with open(flag_path, "w") as f:
            f.write(DYNAMIC_FLAG + "\n")
    except Exception:
        pass

os.environ["FLAG"] = DYNAMIC_FLAG

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "AeroGrid-Avionics-Gateway/2.4.1"
    return response

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/v1/sbom", methods=["GET"])
def sbom():
    """Software Bill of Materials (CycloneDX 1.4 JSON format)."""
    return jsonify({
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": "urn:uuid:8c29bf33-2891-4e78-90b1-aerogrid-sbom",
        "version": 1,
        "metadata": {
            "component": {
                "name": "aerogrid-avionics-telemetry-gateway",
                "version": "2.4.1",
                "type": "application",
                "description": "Real-Time Aerospace Sensor Ingestion & Telemetry Processing Core"
            }
        },
        "components": [
            {
                "type": "library",
                "name": "Flask",
                "version": "3.0.0",
                "purl": "pkg:pypi/flask@3.0.0"
            },
            {
                "type": "library",
                "name": "Werkzeug",
                "version": "3.0.1",
                "purl": "pkg:pypi/werkzeug@3.0.1"
            },
            {
                "type": "library",
                "name": "Jinja2",
                "version": "3.1.2",
                "purl": "pkg:pypi/jinja2@3.1.2"
            },
            {
                "type": "library",
                "name": "PyYAML",
                "version": "5.3.1",
                "purl": "pkg:pypi/pyyaml@5.3.1",
                "description": "YAML parser and emitter for Python (Legacy telemetry manifest ingestion engine)",
                "externalReferences": [
                    {
                        "type": "vulnerability",
                        "url": "https://nvd.nist.gov/vuln/detail/CVE-2020-14343",
                        "comment": "Arbitrary Code Execution through untrusted YAML deserialization via default FullLoader/Loader"
                    }
                ]
            }
        ]
    })

SAMPLE_MANIFEST = """flight_id: "AG-8821"
aircraft_model: "Boeing 787-9 Dreamliner"
carrier: "AeroGrid Global Airlines"
avionics_status: "NOMINAL"
telemetry_metrics:
  altitude_ft: 34500
  airspeed_knots: 485
  fuel_flow_pph: 5200
  engine_temp_c: 642
  cabin_pressure_psi: 11.2
sensors:
  - id: "SEN-01"
    type: "Pitot Static Tube"
    status: "CALIBRATED"
  - id: "SEN-02"
    type: "Angle of Attack Sensor"
    status: "ONLINE"
"""

@app.route("/api/v1/telemetry/sample", methods=["GET"])
def get_sample():
    return jsonify({"success": True, "manifest": SAMPLE_MANIFEST})

def format_parsed_output(obj):
    if hasattr(obj, "read") and callable(obj.read):
        try:
            return obj.read()
        except Exception:
            pass
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, (dict, list, str, int, float, bool)) or obj is None:
        return obj
    return str(obj)

@app.route("/api/v1/telemetry/parse", methods=["POST"])
def parse_telemetry():
    raw_yaml = ""
    if request.is_json:
        raw_yaml = request.json.get("manifest", "")
    elif "manifest" in request.form:
        raw_yaml = request.form.get("manifest", "")
    elif "file" in request.files:
        raw_yaml = request.files["file"].read().decode("utf-8", errors="replace")

    if not raw_yaml.strip():
        return jsonify({"success": False, "error": "Empty telemetry manifest provided."}), 400

    try:
        # VULNERABILITY: Using vulnerable PyYAML 5.3.1 Loader
        parsed = yaml.load(raw_yaml, Loader=yaml.Loader)
        output = format_parsed_output(parsed)
        return jsonify({
            "success": True,
            "message": "Telemetry manifest parsed successfully by AeroGrid Engine.",
            "data": output
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Telemetry Ingestion Parser Error: {str(e)}"
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
