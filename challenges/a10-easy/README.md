# A10 Easy: Information Disclosure Through Errors (QuantEdge Capital)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Easy (Hard-Calibrated Multi-Page Target)
* **Default Port:** 6028
* **Concept:** Unhandled Exception Tracebacks, Internal Stack Frames, Sensitive Token Disclosure

---

### Challenge Description
QuantEdge Capital operates a high-frequency algorithmic risk optimization platform. Data analysts submit portfolio covariance factors to calculate volatility metrics.

However, unexpected runtime inputs (such as zero in mathematical denominators) trigger unhandled exceptions in the calculation engine. Because the platform runs in verbose error disclosure mode, the resulting stack trace exposes internal local frame variables, system file paths, and administrative access tokens.

### Objective
1. Visit the Portfolio Optimizer at `/portfolio`.
2. Provide input that triggers an unhandled zero division exception (`covariance_factor = 0`).
3. Inspect the returned stack trace and extract the internal confidential endpoint and `INTERNAL_VAULT_TOKEN`.
4. Access the internal vault endpoint to retrieve the dynamic flag.
