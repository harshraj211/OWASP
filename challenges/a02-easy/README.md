# A02 Easy: Exposed Sensitive Files & Debug Console

### Category: OWASP Top 10:2025 - A02 Security Misconfiguration
* **Difficulty:** Easy
* **Concept:** Exposed Version Control (.git) & Staging Backup Configurations (.env.backup)

---

### Challenge Description
The RedTeam Hacker Academy Cloud Gateway was deployed to a staging mirror with development artifacts left enabled. 
DevOps engineers inadvertently synced version control history and backup configuration files into the publicly reachable document root.

### Objective
Enumerate the exposed web server files, recover the decommissioned DevOps master vault token from Git commit history or backup environment files, and authenticate to `/api/v1/vault/flag` to retrieve the flag.
