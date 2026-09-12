# A08 Medium: Insecure Update Mechanism (VortexEdge SCADA Gateway)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Medium (Very Difficult Level)
* **Default Port:** 6023
* **Concept:** Unsigned Firmware Packages, Insecure OTA Update Mirror Hijack, Post-Install Script Execution

---

### Challenge Description
VortexEdge SCADA Gateways coordinate telemetry across industrial high-voltage substations. To support remote field maintenance, the gateway includes an Over-The-Air (OTA) firmware upgrade mechanism.

However, the update daemon downloads `.tar.gz` packages over unauthenticated channels without cryptographic signature verification (GPG/Ed25519) and automatically executes `post_install.sh` scripts contained in the package. An attacker who controls the update mirror or uploads a rogue update package can achieve arbitrary command execution.

### Objective
1. Inspect the gateway interface, network configuration (`/settings/network`), and firmware dashboard (`/settings/firmware`).
2. Construct a malicious `.tar.gz` update package containing a `post_install.sh` script that dumps the dynamic flag from `/flag.txt` or the `$FLAG` environment variable.
3. Deploy the malicious firmware package via direct staging upload or by pointing the OTA mirror to an attacker-controlled endpoint.
4. Read the execution logs at `/settings/firmware` or `/settings/logs` to retrieve the dynamic flag.
