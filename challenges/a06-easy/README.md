# A06 Easy - Negative Price Purchase

Self-contained PHP implementation of the OWASP A06:2025 easy lab from the architecture blueprint.

## Run

```bash
docker compose up -d --build
```

Open `http://127.0.0.1:8086`. To use another port:

```bash
APP_PORT=8090 docker compose up -d --build
```

## Reset

The reset button clears the current browser session. A complete platform reset is deterministic:

```bash
docker compose down -v
docker compose up -d
```

## Dynamic flag configuration

The challenge generates a unique, dynamic flag for each individual player / instance by default (`CTF{negative_price_positive_profit_<hex>}`).

You can customize the flag behavior using environment variables:

1. **Automatic Dynamic Flag (Default)**: If no environment variable is passed, a cryptographically random dynamic flag is generated for each individual container / session.
2. **Deterministic Dynamic Flag by User/Student ID**:
   ```bash
   USER_SEED='student_alice' docker compose up -d --build
   ```
3. **Explicit Flag Injection**:
   ```bash
   CTF_FLAG='CTF{custom_platform_flag_here}' docker compose up -d --build
   ```

## Integration contract

- Container HTTP port: `80`
- Health endpoint: `GET /health.php` returns `200 OK` with body `OK`
- Persistent volumes: none
- Required external services: none
- Reverse-proxy compatible: yes; all application URLs are relative
- Player state: isolated by PHP session cookie
- Expected memory footprint: one PHP Apache container

`CHALLENGE.md` contains the player-facing scenario. Author walkthroughs and validation material are distributed separately from the challenge package.
