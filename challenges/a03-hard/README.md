# A03 Hard: Enterprise SIEM Log4Shell / JNDI Supply Chain Ingestion

### Category: OWASP Top 10:2025 - A03 Software Supply Chain Failures
* **Difficulty:** Hard
* **Default Port:** 6009
* **Concept:** Log4Shell Supply Chain Ingestion, Advanced WAF Filter Evasion, Asynchronous SIEM Log Processing

---

### Challenge Description
The KubeShield Enterprise Cloud SIEM Gateway ingests distributed audit telemetry across production Kubernetes clusters. 
Incoming requests pass through an Edge Gateway enforcing Core Rule Set (CRS) inspection to filter out known exploit patterns and signatures.

Downstream from the gateway, events are forwarded to an asynchronous enterprise logging engine that processes and evaluates telemetry expressions. Because the gateway enforces strict filtering on literal exploit strings, direct evaluation requests are rejected with `403 Forbidden`.

Furthermore, in accordance with asynchronous enterprise pipeline design, the ingestion endpoint buffers events and returns `202 Accepted`. To inspect the evaluated log entries and analyze the behavior of the processing sink, auditors must monitor the SIEM Live Audit Stream (`/api/v1/audit/logs`).

### Objective
1. Probe the telemetry ingestion gateway to determine the WAF filtering behavior and identify prohibited keywords.
2. Formulate an advanced expression that circumvents the edge WAF pattern matching while remaining semantically valid for the downstream recursive logging evaluator.
3. Leverage variable substitution or directory resolution to extract the dynamic flag from `/flag.txt`, `/tmp/flag.txt`, or the runtime environment.
4. Retrieve the flag from the SIEM Live Audit Stream.
