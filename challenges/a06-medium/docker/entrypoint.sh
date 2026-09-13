#!/bin/bash
set -e

FLAG_FILE="/var/www/flag.txt"

if [ ! -s "$FLAG_FILE" ]; then
    if [ -n "$CTF_FLAG" ] && [ "$CTF_FLAG" != "CTF{checkout_complete_payment_incomplete}" ]; then
        echo -n "$CTF_FLAG" > "$FLAG_FILE"
    elif [ -n "$USER_SEED" ] || [ -n "$USER_ID" ]; then
        SEED="${USER_SEED:-$USER_ID}"
        HASH=$(echo -n "a06_medium_salt_4812:${SEED}" | sha256sum | head -c 16)
        echo -n "CTF{checkout_complete_payment_${HASH}}" > "$FLAG_FILE"
    else
        RAND_TOKEN=$(head -c 8 /dev/urandom | od -An -tx1 | tr -d ' \n')
        echo -n "CTF{checkout_complete_payment_${RAND_TOKEN}}" > "$FLAG_FILE"
    fi
    chown www-data:www-data "$FLAG_FILE" 2>/dev/null || true
    chmod 644 "$FLAG_FILE" 2>/dev/null || true
fi

exec apache2-foreground "$@"
