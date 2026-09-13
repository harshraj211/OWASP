"""A03 Medium: Software Supply Chain Failures - Dual-Registry Dependency Confusion & Package Poisoning.

Realistic Enterprise Scenario:
FinGuard Corporation's microservices CI/CD pipeline builds the 'finguard-clearing-engine' service.
The build system resolves dependencies against both an internal private registry and an upstream public mirror.
Proprietary modules under the '@finguard/' scope are restricted to the internal registry.
However, an internal telemetry package 'finguard-metrics-collector' was left unscoped in the dependency manifest.
A security auditor or adversary who enumerates the build manifest and historical build output can discover the
unscoped package and register a higher compatible version on the public staging mirror with a postinstall lifecycle script.
"""

import os
import re
import secrets
import subprocess
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_file

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CHALLENGE_KEY = "a03-medium"
PORT = int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or 6008)

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

# Internal private registry packages (hosted on npm.internal.finguard.net)
INTERNAL_PACKAGES = {
    "@finguard/vault-core": {
        "version": "3.1.0",
        "scoped": True,
        "description": "Enterprise cryptographic HSM interface",
        "install_hook": "echo '[BUILD-HOOK] Linking @finguard/vault-core dynamic bindings...'"
    },
    "@finguard/transaction-crypto": {
        "version": "2.0.4",
        "scoped": True,
        "description": "Financial payload signing and integrity verification",
        "install_hook": "echo '[BUILD-HOOK] Compiling transaction crypto algorithms...'"
    },
    "finguard-metrics-collector": {
        "version": "1.1.0",
        "scoped": False,
        "description": "Internal APM telemetry and metrics reporter",
        "install_hook": "echo '[BUILD-HOOK] Initializing finguard-metrics-collector v1.1.0...'"
    }
}

# Public upstream mirror packages (hosted on registry.public-staging.net)
PUBLIC_PACKAGES = {
    "express": {
        "version": "4.19.2",
        "description": "Fast, unopinionated, minimalist web framework",
        "install_hook": "echo '[NPM] express@4.19.2 unpacked.'"
    },
    "helmet": {
        "version": "7.1.0",
        "description": "Help secure Express apps with various HTTP headers",
        "install_hook": "echo '[NPM] helmet@7.1.0 unpacked.'"
    },
    "dotenv": {
        "version": "16.4.5",
        "description": "Loads environment variables from .env for Node.js",
        "install_hook": "echo '[NPM] dotenv@16.4.5 unpacked.'"
    }
}

def parse_semver(v_str):
    clean = re.sub(r"[^\d.]", "", str(v_str)).strip(".")
    parts = clean.split(".") if clean else ["0"]
    result = []
    for p in parts[:3]:
        try:
            result.append(int(p))
        except ValueError:
            result.append(0)
    while len(result) < 3:
        result.append(0)
    return tuple(result)

BUILD_COUNTER = 482
BUILD_LOGS = [
    {
        "id": 481,
        "target": "finguard-clearing-engine:v2.4.0",
        "status": "SUCCESS",
        "timestamp": "2026-09-12 04:15:00",
        "log": """[PIPELINE] Initializing build worker in sandbox environment (ID: runner-k8s-pod-92a1)
[CHECKOUT] Checked out commit 7f8a109 (branch: main)
[PACKAGE] Parsing manifest /workspace/finguard-clearing-engine/package.json
[REGISTRY-CONFIG] Scoped registry mapping detected:
  @finguard/* -> https://npm.internal.finguard.net
  default     -> https://registry.public-staging.net
[FETCH] Resolving dependency graph (6 packages)...
[FETCH] -> @finguard/vault-core@^3.1.0 : matched internal @finguard/vault-core@3.1.0
[FETCH] -> @finguard/transaction-crypto@^2.0.4 : matched internal @finguard/transaction-crypto@2.0.4
[FETCH] -> express@^4.19.2 : resolved from https://registry.public-staging.net/express (4.19.2)
[FETCH] -> helmet@^7.1.0 : resolved from https://registry.public-staging.net/helmet (7.1.0)
[FETCH] -> dotenv@^16.4.5 : resolved from https://registry.public-staging.net/dotenv (16.4.5)
[FETCH] -> finguard-metrics-collector@>=1.1.0 : querying public registry https://registry.public-staging.net/finguard-metrics-collector...
[FETCH]    Not found in public registry (HTTP 404). Falling back to internal repository.
[FETCH]    Matched internal finguard-metrics-collector@1.1.0
[INSTALL] Executing package lifecycle hooks...
> @finguard/vault-core@3.1.0 postinstall
[BUILD-HOOK] Linking @finguard/vault-core dynamic bindings...
> @finguard/transaction-crypto@2.0.4 postinstall
[BUILD-HOOK] Compiling transaction crypto algorithms...
> finguard-metrics-collector@1.1.0 postinstall
[BUILD-HOOK] Initializing finguard-metrics-collector v1.1.0...
[COMPILE] TypeScript compilation completed: 0 errors.
[DOCKER] Container image built successfully: finguard-clearing-engine:v2.4.0 (sha256:7b910e3)
[PIPELINE] Job completed with status: SUCCESS."""
    }
]

@app.after_request
def add_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "FinGuard-CI-Runner/3.2"
    return response

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api/v1/builds", methods=["GET"])
def list_builds():
    summary = [{"id": b["id"], "target": b["target"], "status": b["status"], "timestamp": b["timestamp"]} for b in BUILD_LOGS]
    return jsonify({"success": True, "builds": summary})

@app.route("/api/v1/builds/<int:build_id>/log", methods=["GET"])
def get_build_log(build_id):
    b = next((x for x in BUILD_LOGS if x["id"] == build_id), None)
    if not b:
        return jsonify({"success": False, "error": "Build not found."}), 404
    return jsonify({"success": True, "build_id": build_id, "log": b["log"]})

@app.route("/api/v1/workspace/manifest", methods=["GET"])
def get_manifest():
    """Returns the microservice package.json and .npmrc configuration."""
    return jsonify({
        "package.json": {
            "name": "finguard-clearing-engine",
            "version": "2.4.0",
            "private": True,
            "dependencies": {
                "@finguard/vault-core": "^3.1.0",
                "@finguard/transaction-crypto": "^2.0.4",
                "express": "^4.19.2",
                "helmet": "^7.1.0",
                "dotenv": "^16.4.5",
                "finguard-metrics-collector": ">=1.1.0"
            }
        },
        ".npmrc": "@finguard:registry=https://npm.internal.finguard.net\nregistry=https://registry.public-staging.net\n"
    })

@app.route("/api/v1/registry/public", methods=["GET"])
def list_public_packages():
    return jsonify({"success": True, "packages": PUBLIC_PACKAGES})

@app.route("/api/v1/registry/publish", methods=["POST"])
def publish_public_package():
    data = request.get_json() or {}
    pkg_name = str(data.get("name", "")).strip().lower()
    version = str(data.get("version", "")).strip()
    description = str(data.get("description", "")).strip()
    install_hook = str(data.get("install_hook", "")).strip()

    if not pkg_name:
        return jsonify({"success": False, "error": "Package name is required."}), 400
    if pkg_name.startswith("@finguard/"):
        return jsonify({
            "success": False,
            "error": f"Permission Denied: Namespace '@finguard' is an authenticated enterprise scope and cannot be published to the public registry."
        }), 403
    if not version:
        return jsonify({"success": False, "error": "Package version is required."}), 400

    PUBLIC_PACKAGES[pkg_name] = {
        "version": version,
        "description": description or "Community package publication",
        "install_hook": install_hook or f"echo '[NPM] {pkg_name}@{version} installed.'",
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return jsonify({
        "success": True,
        "message": f"Package '{pkg_name}@{version}' published to https://registry.public-staging.net"
    })

@app.route("/api/v1/build/trigger", methods=["POST"])
def trigger_build():
    global BUILD_COUNTER
    BUILD_COUNTER += 1
    build_id = BUILD_COUNTER

    log_lines = [
        f"[PIPELINE] Initializing build worker in sandbox environment (ID: runner-k8s-pod-{secrets.token_hex(2)})",
        f"[CHECKOUT] Checked out commit {secrets.token_hex(4)} (branch: main)",
        "[PACKAGE] Parsing manifest /workspace/finguard-clearing-engine/package.json",
        "[REGISTRY-CONFIG] Scoped registry mapping detected:",
        "  @finguard/* -> https://npm.internal.finguard.net",
        "  default     -> https://registry.public-staging.net",
        "[FETCH] Resolving dependency graph (6 packages)...",
        "[FETCH] -> @finguard/vault-core@^3.1.0 : matched internal @finguard/vault-core@3.1.0",
        "[FETCH] -> @finguard/transaction-crypto@^2.0.4 : matched internal @finguard/transaction-crypto@2.0.4",
        "[FETCH] -> express@^4.19.2 : resolved from https://registry.public-staging.net/express (4.19.2)",
        "[FETCH] -> helmet@^7.1.0 : resolved from https://registry.public-staging.net/helmet (7.1.0)",
        "[FETCH] -> dotenv@^16.4.5 : resolved from https://registry.public-staging.net/dotenv (16.4.5)"
    ]

    target_pkg = "finguard-metrics-collector"
    internal_meta = INTERNAL_PACKAGES.get(target_pkg)
    public_meta = PUBLIC_PACKAGES.get(target_pkg)

    selected_meta = None
    selected_source = ""

    if public_meta:
        pub_ver = parse_semver(public_meta["version"])
        int_ver = parse_semver(internal_meta["version"])
        log_lines.append(f"[FETCH] -> {target_pkg}@>=1.1.0 : querying public registry https://registry.public-staging.net/{target_pkg}...")
        log_lines.append(f"[FETCH]    Discovered upstream package '{target_pkg}@{public_meta['version']}'")

        if pub_ver >= int_ver:
            log_lines.append(f"[FETCH]    Upstream public version ({public_meta['version']}) satisfies requirement (>=1.1.0). Precedence: upstream.")
            selected_meta = public_meta
            selected_source = "PUBLIC"
        else:
            log_lines.append(f"[FETCH]    Upstream version ({public_meta['version']}) is lower than internal cache. Using internal repository.")
            selected_meta = internal_meta
            selected_source = "INTERNAL"
    else:
        log_lines.append(f"[FETCH] -> {target_pkg}@>=1.1.0 : querying public registry https://registry.public-staging.net/{target_pkg}...")
        log_lines.append("    Not found in public registry (HTTP 404). Falling back to internal repository.")
        log_lines.append("    Matched internal finguard-metrics-collector@1.1.0")
        selected_meta = internal_meta
        selected_source = "INTERNAL"

    log_lines.append("[INSTALL] Executing package lifecycle hooks...")
    log_lines.append("> @finguard/vault-core@3.1.0 postinstall")
    log_lines.append("[BUILD-HOOK] Linking @finguard/vault-core dynamic bindings...")
    log_lines.append("> @finguard/transaction-crypto@2.0.4 postinstall")
    log_lines.append("[BUILD-HOOK] Compiling transaction crypto algorithms...")

    hook_command = selected_meta["install_hook"]
    log_lines.append(f"> {target_pkg}@{selected_meta['version']} postinstall")

    try:
        proc = subprocess.run(
            hook_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
            env=dict(os.environ, FLAG=DYNAMIC_FLAG)
        )
        if proc.stdout:
            for out_line in proc.stdout.strip().split("\n"):
                log_lines.append(f"  {out_line}")
        if proc.stderr:
            for err_line in proc.stderr.strip().split("\n"):
                log_lines.append(f"  {err_line}")
    except Exception as e:
        log_lines.append(f"  [HOOK_ERROR] {str(e)}")

    log_lines.append("[COMPILE] TypeScript compilation completed: 0 errors.")
    log_lines.append(f"[DOCKER] Container image built successfully: finguard-clearing-engine:v2.4.0 (sha256:{secrets.token_hex(4)})")
    log_lines.append("[PIPELINE] Job completed with status: SUCCESS.")

    full_log = "\n".join(log_lines)
    record = {
        "id": build_id,
        "target": "finguard-clearing-engine:v2.4.0",
        "status": "SUCCESS",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "log": full_log
    }
    BUILD_LOGS.insert(0, record)

    return jsonify({
        "success": True,
        "build_id": build_id,
        "status": "SUCCESS",
        "log": full_log
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
