# A08 Hard: Unsafe Deserialization (AeroData Analytics)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Hard (Insanely Hard Level)
* **Default Port:** 6024
* **Concept:** Python Pickle Deserialization Sandbox Evasion, Blocklist Bypass, Code Execution

---

### Challenge Description
AeroData Analytics provides high-throughput stream processing for international flight telemetry. To enable data engineers to save and share transformation pipelines, the platform serializes execution graphs into Base64-encoded tokens.

When importing saved pipelines (`/pipeline/import`), the server deserializes the graph using a custom `pickle.Unpickler`. The security policy enforces a blocklist rejecting `os`, `subprocess`, `posix`, `sys`, and `commands`.

### Objective
Bypass the restricted unpickler's module blocklist using allowed execution primitives (e.g. `builtins.eval`), execute code to read the dynamic flag from `/flag.txt`, and retrieve the flag from the deserialization output.
