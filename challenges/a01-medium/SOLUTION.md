# MeridianHR — Author-only solution

The intended account is `alex.employee@meridianhr.local` / `Password123`.

1. Discover `/internal/reports` from `robots.txt` or the legacy bundle. Direct access is blocked by the referer check.
2. Browse to `/account/upgrade/start`, then `/account/upgrade/confirm`. The workflow is only cosmetic.
3. Call `GET /account/upgrade/finalize` (or `POST /account/upgrade/finalize`) directly while authenticated. The missing step/approval checks change the employee's role to `HR_ADMIN`.
4. Open `/admin/dashboard`, then request `/internal/reports` with a referer containing `/admin/dashboard`.
5. Download the dynamically named report and submit the generated `FLAG{...}` value.

Secondary issue: `POST /admin/deleteUser` is a legacy route without the `HR_ADMIN` check that protects the GET route. It is not required for the primary solve.

The HR admin password is generated randomly at startup unless `HR_ADMIN_PASSWORD` is explicitly supplied for development.
