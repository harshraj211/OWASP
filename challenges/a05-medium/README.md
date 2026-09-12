# A05 Medium: Server-Side Request Forgery & DNS Validation Bypass

### Category: OWASP Top 10:2025 - A05 Injection
* **Difficulty:** Medium
* **Default Port:** 6014
* **Concept:** SSRF with Pre-Flight DNS Validation Bypass (HTTP Redirect / TOCTOU)

---

### Challenge Description
The WebPulse Health Inspector probes external URLs and returns response summaries.
To protect internal microservices, the application resolves the requested hostname before fetching it and blocks all loopback (`127.0.0.1`, `::1`) and RFC 1918 private network addresses (`10.0.0.0/8`, `192.168.0.0/16`, etc.).

However, the underlying HTTP client library (`urllib.request.urlopen`) transparently follows HTTP redirects without re-applying the destination IP filter. An internal management endpoint at `/admin/status` restricts access exclusively to loopback callers (`127.0.0.1`).

### Objective
Craft a Server-Side Request Forgery payload utilizing an open HTTP redirect service (or the platform relay) to bypass pre-flight DNS validation, coerce the server into requesting `http://127.0.0.1:<PORT>/admin/status`, and retrieve the dynamic flag.
