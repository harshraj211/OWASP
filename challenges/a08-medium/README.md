# A08 Medium: Insecure Update Mechanism (VortexEdge SCADA Gateway)

### Category: OWASP Top 10:2025 - A08 Software or Data Integrity Failures
* **Difficulty:** Medium (10/10 Calibrated)
* **Default Port:** 6023
* **Concept:** Unsigned Firmware Packages, Firmware Manifest Verification Bypass, Post-Install Script Execution

---

### Challenge Description
VortexEdge SCADA Gateways coordinate telemetry across industrial high-voltage substations. To support remote field maintenance, the gateway includes an Over-The-Air (OTA) firmware upgrade mechanism.

The update daemon verifies that firmware packages contain a valid `firmware.json` manifest specifying the target hardware model (`VortexEdge-GW01`), a higher version (`> v3.1.4`), and an internal SHA-256 checksum matching the post-install script. 

However, the gateway completely lacks **cryptographic digital signature verification (e.g. Ed25519/GPG)** certified by the VortexEdge Root CA. Because anyone can construct a syntactically valid manifest matching their own custom script hash, an attacker can craft a rogue update bundle and achieve arbitrary command execution.

### Objective
1. Inspect the gateway interface, network configuration (`/settings/network`), firmware dashboard (`/settings/firmware`), and system logs (`/settings/logs`).
2. Identify the firmware manifest schema and requirements from system audit logs.
3. Construct a valid `.tar.gz` firmware package containing `firmware.json` and a `post_install.sh` script that dumps the dynamic flag from `/flag.txt` or `$FLAG`.
4. Deploy the firmware package via direct staging upload or through the configured OTA repository mirror.
5. Retrieve the dynamic flag from the execution deployment output.
