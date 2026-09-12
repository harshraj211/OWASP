import os
import secrets
import traceback
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
INTERNAL_VAULT_TOKEN = f"QE_TOKEN_{secrets.token_hex(8)}"

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
def portfolio():
    err_trace = None
    res = None
    if request.method == 'POST':
        assets_raw = request.form.get('assets', 'AAPL, NVDA')
        weights_raw = request.form.get('weights', '0.5, 0.5')
        cov_factor = request.form.get('covariance_factor', '1.0').strip()

        try:
            factor = float(cov_factor)
            # VULNERABILITY: Information Disclosure through Unhandled Exception
            # Supplying 0 triggers a ZeroDivisionError, which dumps detailed stack traces, internal paths, and secrets
            normalized_vol = (0.24 * 0.24) / factor
            res = f"Portfolio Volatility: {normalized_vol:.4f} | Annualized Sharpe: {1.85 / (normalized_vol ** 0.5):.2f}"
        except Exception as e:
            tb = traceback.format_exc()
            # Mimic verbose unhandled debug error page disclosing local variables & paths
            err_trace = (
                f"Traceback (most recent call last):\n"
                f"  File \"/app/core_engine/portfolio_optimizer.py\", line 142, in evaluate_risk\n"
                f"    normalized_vol = (0.24 * 0.24) / factor\n"
                f"ZeroDivisionError: {str(e)}\n\n"
                f"--- Local Frame Variables at Exception ---\n"
                f"factor: {cov_factor}\n"
                f"assets: {assets_raw}\n"
                f"INTERNAL_ENDPOINT: \"/api/v1/internal/confidential-vault\"\n"
                f"INTERNAL_VAULT_TOKEN: \"{INTERNAL_VAULT_TOKEN}\"\n"
                f"FILESYSTEM_PATH: \"/app/core_engine/secrets_manager.py\"\n"
            )
    return render_template('portfolio.html', error_trace=err_trace, calculation_result=res)

@app.route('/vault')
def vault_view():
    return render_template('vault.html', flag=None)

@app.route('/api/v1/internal/confidential-vault')
def internal_vault():
    token = request.args.get('token', '').strip()
    if token and token == INTERNAL_VAULT_TOKEN:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"success": True, "flag": DYNAMIC_FLAG})
        return render_template('vault.html', flag=DYNAMIC_FLAG)
    return jsonify({"success": False, "error": "Unauthorized: Invalid internal vault token."}), 403

if __name__ == '__main__':
    port = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6028)
    print(f"[{CHALLENGE_KEY}] Running on port {port}")
    app.run(host='0.0.0.0', port=port)
