# A02 Medium: OmniRoute Ingress Gateway (Nginx Off-by-Slash)

### Category: OWASP Top 10:2025 - A02 Security Misconfiguration
* **Difficulty:** Medium
* **Port:** 6005
* **Concept:** Reverse Proxy Path Normalization & Internal Microservice Header Spoofing

---

### Challenge Description
An enterprise learning asset distribution service runs behind an ingress reverse proxy.
Static assets are delivered from a designated directory. However, a subtle path normalization discrepancy allows attackers to traverse out of the intended folder, dump backend server configuration, and discover internal cluster authorization keys.
