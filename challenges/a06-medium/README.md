# A06 Medium - Payment Workflow Bypass

Self-contained PHP implementation of the OWASP A06:2025 medium lab.

## Run

```bash
docker compose up -d --build
```

Open `http://127.0.0.1:8088`. Set another host port with `APP_PORT` if required.

## Reset

Use the reset control in the application for the current browser session, or reset the entire lab:

```bash
docker compose down -v
docker compose up -d
```

## Dynamic flag configuration

The challenge generates a unique, dynamic flag for each individual player / instance by default (`CTF{checkout_complete_payment_<hex>}`).

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
- External services: none
- Reverse-proxy compatible: yes; application navigation uses relative paths
- Player state: isolated by PHP session cookie

The challenge package contains no tests or author solution.

