# A05 Hard: Blind Server-Side Template Injection (SSTI & RCE)

### Category: OWASP Top 10:2025 - A05 Injection
* **Difficulty:** Hard
* **Default Port:** 6015
* **Concept:** Blind Jinja2 SSTI with Strict Character and Keyword Filter Evasion

---

### Challenge Description
The Apex Telemetry Engine exposes an endpoint (`/api/telemetry/probe`) that allows operators to validate custom telemetry format expressions. The template string is processed server-side via Jinja2's `render_template_string()`.

The target is hardened with two layers of defense:
1. **Blind Evaluation**: The rendered output is never returned in the HTTP response; the server only reports whether the expression was syntactically valid or failed.
2. **Filter Blacklist**: The input filter drops requests containing `.`, `_`, `[`, `]`, or sensitive execution terms (`class`, `mro`, `base`, `subclasses`, `config`, `self`, `request`, `import`, `builtins`, `os`, `system`, `popen`, `subprocess`, `read`, `write`, `open`).

### Objective
Bypass the Jinja2 sandbox filters using attribute helpers (`|attr`) and format string generators (`'%c'|format(...)`) to access system shell commands via an error-based/boolean side channel (`{{1/0}}` on False), dump the dynamic flag from `/flag.txt`, and submit it to the platform.
