# A08 Hard: Unsafe Deserialization (AeroData Analytics)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Hard (Insanely Hard Level)
* **Default Port:** 6024
* **Concept:** Python Deserialization Sandbox Evasion, Execution Function Restriction Bypass, Arbitrary Object Reconstruction

---

### Challenge Description
AeroData Analytics provides high-throughput stream processing for flight telemetry. To enable data engineers to save and share transformation pipelines, the platform serializes execution graphs into Base64-encoded tokens.

When importing saved pipelines (`/pipeline/import`), the server restores the execution graph using Python deserialization under an internal security sandbox that enforces strict module and execution function restrictions.

### Objective
Analyze the pipeline serialization format, construct an exploit payload that evades the deserialization sandbox filters to access the dynamic flag at `/flag.txt`, and retrieve the flag from the server response.
