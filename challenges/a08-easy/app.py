import os
import sys
import io
import json
import zipfile
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

CHALLENGE_KEY = "a08-easy"

def get_flag():
    f = os.environ.get("FLAG") or os.environ.get("CTF_FLAG")
    if f and f.strip():
        return f.strip()
    return f"RTSA{{{CHALLENGE_KEY}_{secrets.token_hex(12)}}}"

DYNAMIC_FLAG = get_flag()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")
os.makedirs(PLUGINS_DIR, exist_ok=True)

# Write flag to /flag.txt if possible, and app flag.txt
for path in ["/flag.txt", os.path.join(BASE_DIR, "flag.txt")]:
    try:
        with open(path, "w") as f:
            f.write(DYNAMIC_FLAG)
    except Exception:
        pass

DEFAULT_PLUGINS = [
    {"id": "analytics-core", "name": "Google & Plausible Analytics Core", "version": "2.4.1", "integrity": "Signed (Novus CA)"},
    {"id": "seo-optimizer", "name": "Automated Meta & OpenGraph Generator", "version": "1.8.0", "integrity": "Signed (Novus CA)"}
]

INSTALLED_PLUGINS = list(DEFAULT_PLUGINS)

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok", "challenge": CHALLENGE_KEY}), 200

@app.route('/')
def index():
    return render_template('index.html', plugins=INSTALLED_PLUGINS)

@app.route('/articles')
def articles():
    return render_template('articles.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    user = request.form.get('username', '').strip()
    pwd = request.form.get('password', '').strip()

    if user == "editor" and pwd == "EditorNovus2026!":
        session['user'] = user
        session['role'] = "Senior Managing Editor"
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Invalid editorial credentials."), 401

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/admin/plugins')
def plugins_view():
    if not session.get('user'):
        return redirect(url_for('login'))
    out = session.pop('plugin_exec_output', None)
    return render_template('plugins.html', plugins=INSTALLED_PLUGINS, execution_output=out)

@app.route('/admin/plugins/upload', methods=['GET', 'POST'])
def upload_plugin():
    if not session.get('user'):
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('plugin_upload.html')
    
    file = request.files.get('plugin_file')
    if not file or not file.filename.endswith('.zip'):
        return render_template('plugin_upload.html', error="Valid ZIP package required."), 400
    
    try:
        zf = zipfile.ZipFile(file.stream)
        if "manifest.json" not in zf.namelist():
            return render_template('plugin_upload.html', error="Archive missing required manifest.json."), 400
        
        manifest_data = json.loads(zf.read("manifest.json").decode('utf-8'))
        plugin_id = manifest_data.get("id", f"plugin-{secrets.token_hex(4)}")
        plugin_name = manifest_data.get("name", "Custom Extension")
        entrypoint = manifest_data.get("entrypoint", "plugin.py")

        # Flawed integrity verification: allows developer bypass or algorithm 'none'
        v_mode = manifest_data.get("verification_mode")
        v_algo = manifest_data.get("signature_algorithm")
        
        if v_mode != "developer_bypass" and v_algo != "none":
            if "signature" not in manifest_data or not manifest_data.get("signature"):
                return render_template('plugin_upload.html', error="Untrusted plugin: Missing cryptographic signature from Novus CA."), 403

        # Extract files to plugins directory
        dest_dir = os.path.join(PLUGINS_DIR, plugin_id)
        os.makedirs(dest_dir, exist_ok=True)
        zf.extractall(dest_dir)

        INSTALLED_PLUGINS.append({
            "id": plugin_id,
            "name": plugin_name,
            "version": manifest_data.get("version", "1.0.0"),
            "integrity": "Developer Bypass / Unverified" if v_mode else "Custom Signature",
            "entrypoint": os.path.join(dest_dir, entrypoint)
        })

        return redirect(url_for('plugins_view'))
    except Exception as e:
        return render_template('plugin_upload.html', error=f"Extraction error: {str(e)}"), 500

@app.route('/admin/plugins/run/<plugin_id>')
def run_plugin(plugin_id):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    target = next((p for p in INSTALLED_PLUGINS if p["id"] == plugin_id), None)
    if not target:
        return "Plugin not found", 404
    
    entrypoint = target.get("entrypoint")
    if not entrypoint or not os.path.exists(entrypoint):
        session['plugin_exec_output'] = f"Builtin plugin '{target['name']}' executed in background daemon."
        return redirect(url_for('plugins_view'))
    
    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        with open(entrypoint, "r") as f:
            code = f.read()
        exec(code, {"__name__": "__main__", "FLAG": DYNAMIC_FLAG, "os": os})
    except Exception as e:
        print(f"Execution failed with exception: {e}")
    finally:
        sys.stdout = old_stdout
    
    session['plugin_exec_output'] = buf.getvalue().strip() or "Task completed with exit code 0 (no output)."
    return redirect(url_for('plugins_view'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6022)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
