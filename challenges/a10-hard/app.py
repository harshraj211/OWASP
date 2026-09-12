import os
import subprocess
import secrets
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a10-hard"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")
SCRIPTS_DIR = os.path.join(BASE_DIR, "static", "scripts")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Write flag to /flag.txt if possible, and local flag.txt
for path in ["/flag.txt", os.path.join(BASE_DIR, "flag.txt")]:
    try:
        with open(path, "w") as f:
            f.write(DYNAMIC_FLAG)
    except Exception:
        pass

ASSETS = []

class ImageHeaderError(Exception):
    pass

class MalwareDetectedError(Exception):
    pass

def validate_image_header(data):
    # Header format verification
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if b"IHDR" not in data[:32]:
            raise ImageHeaderError("Malformed PNG structure: Corrupted or missing IHDR chunk marker.")
        return "PNG"
    elif data.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "GIF"
    elif data.startswith(b"CORRUPT_RAW_STREAM"):
        raise ImageHeaderError("Decompression/format fault: Unhandled raw image bitstream.")
    else:
        raise ValueError("Unsupported asset format. Only PNG, JPEG, or RAW stream containers allowed.")

def scan_malware(data):
    signatures = [b"eval(", b"system(", b"subprocess", b"popen", b"exec(", b"<?php", b"passthru", b"import os"]
    data_lower = data.lower()
    for sig in signatures:
        if sig in data_lower:
            raise MalwareDetectedError(f"Prohibited executable signature detected: '{sig.decode()}'")

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    scripts = os.listdir(SCRIPTS_DIR)
    return render_template('index.html', staged_scripts=scripts)

@app.route('/articles')
def articles():
    return render_template('articles.html')

@app.route('/media/library')
def library():
    return render_template('library.html', assets=ASSETS)

@app.route('/media/upload', methods=['GET', 'POST'])
def upload_view():
    msg = None
    err = None
    if request.method == 'POST':
        f = request.files.get('asset_file')
        if not f or not f.filename:
            return render_template('upload.html', error="No file attached."), 400
        
        filename = f.filename
        content = f.read()

        try:
            # Stage 1: Validate image headers
            fmt = validate_image_header(content)
            # Stage 2: Deep anti-malware signature scan
            scan_malware(content)

            safe_name = f"{secrets.token_hex(4)}_{secure_filename(filename)}"
            dest = os.path.join(UPLOADS_DIR, safe_name)
            with open(dest, "wb") as out:
                out.write(content)
            
            ASSETS.append({"name": safe_name, "path": f"/static/uploads/{safe_name}", "stage": "Stage 1+2 Verified", "status": "Clean"})
            msg = f"Asset '{safe_name}' verified and published to library."

        except ImageHeaderError as ihe:
            # VULNERABILITY: Mishandling of Exceptional Conditions (Fail-Open File Upload)
            # When an ImageHeaderError occurs during Stage 1 header verification, the server catches
            # the exception and executes a fallback "raw asset staging" path.
            # This completely skips the Stage 2 malware scanner and writes the file using the original
            # filename into the executable scripts directory (static/scripts/)!
            raw_filename = os.path.basename(filename)
            script_path = os.path.join(SCRIPTS_DIR, raw_filename)
            with open(script_path, "wb") as out:
                out.write(content)
            
            ASSETS.append({"name": raw_filename, "path": f"/static/scripts/{raw_filename}", "stage": "Bypassed via Exception", "status": "Staged as Script"})
            msg = f"ImageHeaderError caught ({str(ihe)}). Exception fallback triggered: asset archived to scripts directory as '{raw_filename}'!"

        except MalwareDetectedError as mde:
            err = f"Security Violation: {str(mde)}"
        except Exception as e:
            err = f"Validation Error: {str(e)}"

    return render_template('upload.html', message=msg, error=err)

@app.route('/editorial/terminal')
def terminal_view():
    scripts = os.listdir(SCRIPTS_DIR)
    out = session.pop('terminal_output', None)
    return render_template('terminal.html', staged_scripts=scripts, execution_output=out)

@app.route('/editorial/run-automation', methods=['POST'])
def run_automation():
    name = request.form.get('script_name', '').strip()
    if not name:
        return redirect(url_for('terminal_view'))
    
    target_path = os.path.join(SCRIPTS_DIR, os.path.basename(name))
    if not os.path.exists(target_path):
        session['terminal_output'] = f"Error: Script '{name}' not found in staging."
        return redirect(url_for('terminal_view'))
    
    try:
        proc = subprocess.run(
            ["python3", target_path],
            capture_output=True,
            text=True,
            timeout=10,
            env={"FLAG": DYNAMIC_FLAG, "PATH": "/usr/local/bin:/usr/bin:/bin"}
        )
        session['terminal_output'] = proc.stdout.strip() or proc.stderr.strip() or "Script executed with exit code 0."
    except Exception as e:
        session['terminal_output'] = f"Execution Exception: {str(e)}"
    
    return redirect(url_for('terminal_view'))

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6030)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
