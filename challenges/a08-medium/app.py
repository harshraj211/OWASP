import os
import tarfile
import secrets
import subprocess
import shutil
import urllib.request
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a08-medium"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STAGING_DIR = os.path.join(BASE_DIR, "staging")
os.makedirs(STAGING_DIR, exist_ok=True)

# Write flag to /flag.txt if possible, and app flag.txt
for path in ["/flag.txt", os.path.join(BASE_DIR, "flag.txt")]:
    try:
        with open(path, "w") as f:
            f.write(DYNAMIC_FLAG)
    except Exception:
        pass

CONFIG = {
    "hostname": "vortex-substation-gw01",
    "current_version": "v3.1.4",
    "update_mirror": "http://127.0.0.1:6023/mock-repo/package.tar.gz"
}

SYSTEM_LOGS = [
    "[SYSTEM] VortexEdge SCADA Substation Gateway Initialized.",
    "[SYSTEM] Modbus TCP Channel Poller running on port 502.",
    "[SECURITY] OTA Integrity Monitor: Unauthenticated HTTP mirrors permitted for local field service."
]

def log_event(msg):
    SYSTEM_LOGS.append(f"[EVENT] {msg}")

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html', **CONFIG)

@app.route('/telemetry')
def telemetry():
    return render_template('telemetry.html')

@app.route('/settings/network', methods=['GET', 'POST'])
def network_settings():
    msg = None
    if request.method == 'POST':
        CONFIG['hostname'] = request.form.get('hostname', CONFIG['hostname']).strip()
        CONFIG['update_mirror'] = request.form.get('update_mirror', CONFIG['update_mirror']).strip()
        log_event(f"Network configuration updated: OTA Mirror set to {CONFIG['update_mirror']}")
        msg = "Configuration saved successfully."
    return render_template('network.html', message=msg, **CONFIG)

@app.route('/settings/firmware')
def firmware_view():
    res = session.pop('update_result', None)
    return render_template('firmware.html', update_result=res, **CONFIG)

@app.route('/settings/logs')
def logs_view():
    return render_template('logs.html', logs=SYSTEM_LOGS[-30:])

def execute_firmware_archive(tar_path):
    """Unpack archive and execute post_install.sh without authenticity verification."""
    unpack_dir = os.path.join(STAGING_DIR, f"upgrade_{secrets.token_hex(4)}")
    os.makedirs(unpack_dir, exist_ok=True)
    try:
        with tarfile.open(tar_path, "r:*") as tf:
            tf.extractall(unpack_dir)
        
        script = None
        for candidate in ["post_install.sh", "install.sh", "upgrade.sh"]:
            target = os.path.join(unpack_dir, candidate)
            if os.path.exists(target):
                script = target
                break
        
        if not script:
            return "Upgrade failed: No post_install.sh script found in update package."
        
        os.chmod(script, 0o755)
        # Execute upgrade script
        proc = subprocess.run(
            ["bash", script],
            cwd=unpack_dir,
            capture_output=True,
            text=True,
            timeout=10,
            env={"FLAG": DYNAMIC_FLAG, "PATH": "/usr/local/bin:/usr/bin:/bin"}
        )
        output = proc.stdout.strip()
        if proc.stderr:
            output += "\n[STDERR] " + proc.stderr.strip()
        log_event(f"Firmware upgrade script executed. Exit code: {proc.returncode}")
        return output or "Upgrade script executed cleanly (0 bytes stdout)."
    except Exception as e:
        log_event(f"Upgrade execution error: {str(e)}")
        return f"Error executing update: {str(e)}"
    finally:
        shutil.rmtree(unpack_dir, ignore_errors=True)

@app.route('/api/v1/staging/upload', methods=['POST'])
def staging_upload():
    f = request.files.get('firmware_file')
    if not f:
        session['update_result'] = "Upload failed: No package file attached."
        return redirect(url_for('firmware_view'))
    
    tmp_path = os.path.join(STAGING_DIR, f"upload_{secrets.token_hex(4)}.tar.gz")
    f.save(tmp_path)
    output = execute_firmware_archive(tmp_path)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    session['update_result'] = output
    return redirect(url_for('firmware_view'))

@app.route('/api/v1/update/apply', methods=['POST'])
def update_apply():
    mirror = request.form.get('update_url') or CONFIG['update_mirror']
    log_event(f"Fetching OTA update package from {mirror}...")
    tmp_path = os.path.join(STAGING_DIR, f"download_{secrets.token_hex(4)}.tar.gz")
    try:
        req = urllib.request.Request(mirror, headers={"User-Agent": "VortexEdge-OTAFirmware/3.1"})
        with urllib.request.urlopen(req, timeout=5) as resp, open(tmp_path, "wb") as out:
            shutil.copyfileobj(resp, out)
        output = execute_firmware_archive(tmp_path)
        session['update_result'] = output
    except Exception as e:
        session['update_result'] = f"Failed to download or apply OTA package: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return redirect(url_for('firmware_view'))

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6023)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
