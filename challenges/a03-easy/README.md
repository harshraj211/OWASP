# A03 Easy: Known Component CVE & SBOM Dependency Audit

### Category: OWASP Top 10:2025 - A03 Software Supply Chain Failures
* **Difficulty:** Easy
* **Default Port:** 6007
* **Concept:** Insecure Deserialization via Known Third-Party Component CVE (CVE-2020-14343) & SBOM Audit

---

### Challenge Description
The AeroGrid Avionics Fleet Telemetry Gateway ingests and visualizes black-box flight telemetry manifests from commercial aircraft. 
To maintain supply chain transparency under modern aerospace DevSecOps regulations, the server exposes a machine-readable Software Bill of Materials (SBOM) at `/api/v1/sbom`.

Deep within the ingestion pipeline, the service uses an outdated version of the **PyYAML** library (`5.3.1`) configured with the default `Loader=yaml.Loader` constructor. This version is vulnerable to **CVE-2020-14343**, enabling remote code execution and arbitrary function evaluation via untrusted YAML tags.

### Objective
1. Inspect the Software Bill of Materials at `/api/v1/sbom` to identify the vulnerable component and version.
2. Research the corresponding CVE to craft a weaponized YAML telemetry manifest using `!!python/object/apply:subprocess.check_output` or `!!python/object/apply:os.popen`.
3. Submit the payload through `/api/v1/telemetry/parse` to read the dynamic flag from `/flag.txt` or environment variable `FLAG`.
