# A01 Easy — Horizontal IDOR

This container is an intentionally vulnerable training target. It models a
student-record portal that authenticates a student session but fails to enforce
that the requested record belongs to the signed-in student. Document IDs,
including the executive record, are generated per instance.

## Run locally

Provide a new flag for every instance; no flag is baked into the image.

```sh
docker build -t oswap-a01-easy challenges/a01-easy
docker run --rm -p 127.0.0.1:6001:5000 \
  -e FLAG="RTSA{replace_with_a_unique_value}" \
  oswap-a01-easy
```

Open `http://127.0.0.1:6001`. The health check is available at `/healthz`.

## Maintainer notes

- The only intentional vulnerability is the missing object-ownership check in
  `get_record`; all other authentication/session behavior is supporting lab
  infrastructure.
- The application generates a random fallback flag only for direct local runs;
  the platform should always inject `FLAG` per launched instance.
- Do not expose this deliberately vulnerable container to an untrusted network.
