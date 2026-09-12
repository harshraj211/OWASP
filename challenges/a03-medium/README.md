# A03 Medium: Dual-Registry Dependency Confusion & Package Poisoning

### Category: OWASP Top 10:2025 - A03 Software Supply Chain Failures
* **Difficulty:** Medium
* **Default Port:** 6008
* **Concept:** Multi-Registry Dependency Confusion, Unscoped Internal Dependency Hijacking & Lifecycle Execution

---

### Challenge Description
FinGuard Corporation maintains an automated CI/CD microservice build cluster for financial settlement services. 
When building container images, the build runner pulls dependencies from both:
- An internal private repository (`npm.internal.finguard.net`)
- An upstream public mirror (`registry.public-staging.net`)

Security researchers have noted that inconsistent namespace scoping in multi-registry environments can lead to **Dependency Confusion**. If an internal package is not protected by an organization scope in the package manifest and configuration, an external registry holding a package with the same name and higher version precedence will be resolved instead.

### Objective
1. Inspect the CI/CD pipeline history and workspace manifest to audit the dependency resolution process.
2. Identify the internal unpinned/unscoped package and its version constraints.
3. Publish a package to the public staging mirror that satisfies the requirement while taking precedence over the internal repository, utilizing an installation lifecycle hook to read the dynamic flag from `/flag.txt`, `/tmp/flag.txt`, or environment variable `FLAG`.
4. Trigger the build pipeline and extract the flag from the build worker logs.
