#!/usr/bin/env bash
set -euo pipefail

category="${1:-}"
level="${2:-}"
category="${category,,}"
level="${level,,}"
challenge_key="${category}-${level}"
challenge_dir="$(cd "$(dirname "$0")/../challenges/$challenge_key" && pwd)"
container_name="oswap-active-challenge"
image_name="oswap-${challenge_key}:latest"
cat_num="$(echo "$category" | grep -o '[0-9]\+' | sed 's/^0*//')"
cat_num="${cat_num:-1}"
offset=0
if [[ "$level" == "medium" ]]; then
    offset=1
elif [[ "$level" == "hard" ]]; then
    offset=2
fi
port=$(( 6000 + (cat_num - 1) * 3 + 1 + offset ))

if [[ ! -f "$challenge_dir/Dockerfile" ]]; then
    echo "Challenge is not installed: $challenge_key" >&2
    exit 1
fi

docker rm -f "$container_name" >/dev/null 2>&1 || true
old_pid="$(cat /tmp/oswap-active-challenge.pid 2>/dev/null || true)"
if [[ "$old_pid" =~ ^[0-9]+$ ]]; then
    kill "$old_pid" >/dev/null 2>&1 || true
    rm -f /tmp/oswap-active-challenge.pid
fi
fuser -k "${port}/tcp" >/dev/null 2>&1 || true

flag="RTSA{${challenge_key}_$(openssl rand -hex 12)}"

mode="docker"
if docker info >/dev/null 2>&1; then
    source_hash="$(find "$challenge_dir" -type f ! -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}')"
    image_hash="$(docker image inspect --format '{{index .Config.Labels "org.oswap.source-hash"}}' "$image_name" 2>/dev/null || true)"
    if [[ "$image_hash" != "$source_hash" ]]; then
        docker build --label "org.oswap.source-hash=${source_hash}" --tag "$image_name" "$challenge_dir"
    fi
    docker run --detach --name "$container_name" \
        --cap-add NET_ADMIN \
        --publish "127.0.0.1:${port}:${port}" \
        --env "FLAG=${flag}" \
        "$image_name" >/dev/null
    for _ in {1..30}; do
        running="$(docker inspect --format '{{.State.Running}}' "$container_name" 2>/dev/null || true)"
        if [[ "$running" == "true" ]]; then
            if python3 -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:${port}/healthz', timeout=1)" >/dev/null 2>&1; then
                break
            fi
        else
            break
        fi
        sleep 0.25
    done
    running="$(docker inspect --format '{{.State.Running}}' "$container_name" 2>/dev/null || true)"
    if [[ "$running" != "true" ]]; then
        docker logs "$container_name" >&2 || true
        docker rm -f "$container_name" >/dev/null 2>&1 || true
        echo "Container failed to start: $challenge_key" >&2
        exit 1
    fi
else
    mode="process"
    echo "Docker is unavailable; starting the lab as a local process." >&2
    old_pid="$(cat /tmp/oswap-active-challenge.pid 2>/dev/null || true)"
    if [[ "$old_pid" =~ ^[0-9]+$ ]]; then
        kill "$old_pid" >/dev/null 2>&1 || true
    fi
    if [[ -f "$challenge_dir/app.py" ]]; then
        FLAG="$flag" LAB_PORT="$port" setsid nohup python3 "$challenge_dir/app.py" \
            >/tmp/oswap-active-challenge.log 2>&1 &
    elif [[ -f "$challenge_dir/app.js" ]]; then
        FLAG="$flag" PORT="$port" setsid nohup node "$challenge_dir/app.js" \
            >/tmp/oswap-active-challenge.log 2>&1 &
    fi
    echo $! >/tmp/oswap-active-challenge.pid
    pid="$!"
    for _ in {1..20}; do
        if kill -0 "$pid" >/dev/null 2>&1; then
            if python3 -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:${port}/healthz', timeout=1)" >/dev/null 2>&1; then
                break
            fi
        fi
        sleep 0.25
    done
    if ! python3 -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:${port}/healthz', timeout=1)" >/dev/null 2>&1; then
        cat /tmp/oswap-active-challenge.log >&2 || true
        kill "$pid" >/dev/null 2>&1 || true
        exit 1
    fi
fi

tmp_state="$(mktemp /tmp/active_lab.XXXXXX)"
printf '{\n  "running": true,\n  "challenge": "%s",\n  "port": %s,\n  "flag": "%s"\n}\n' \
    "$challenge_key" "$port" "$flag" > "$tmp_state"
if [[ "$mode" == "process" ]]; then
    python -c "import json; p='/tmp/active_lab.json'; d=json.load(open('$tmp_state')); d['mode']='process'; d['pid']=int(open('/tmp/oswap-active-challenge.pid').read()); json.dump(d, open('$tmp_state','w'))"
fi
mv "$tmp_state" /tmp/active_lab.json
echo "Lab ${challenge_key} launched successfully on port ${port}"
