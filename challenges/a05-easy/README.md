# A05 Easy: SQL Injection Authentication Bypass (WAF Evasion)

### Category: OWASP Top 10:2025 - A05 Injection
* **Difficulty:** Easy
* **Default Port:** 6013
* **Concept:** SQL Injection with Hard WAF Evasion (No Spaces, No Comments, No OR/AND, No =)

---

### Challenge Description
The RedTeam Hacker Academy Sovereign Enclave Access Gateway authenticates users using an internal SQLite database.
An aggressive WAF filter pattern blocks common SQL injection tokens:
- Whitespace characters (`\s`)
- All comment syntax (`--`, `#`, `/*`, `*/`)
- Boolean keywords (`OR`, `AND`)
- Standard comparison operators (`=`, `LIKE`)

Despite these constraints, the SQL query interpolates user strings directly into the statement.

### Objective
Bypass the WAF filtering constraints using SQLite functions and subquery wrappers to authenticate as the `admin` user (role: `administrator`) and retrieve the dynamic flag.
