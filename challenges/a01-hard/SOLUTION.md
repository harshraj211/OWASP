# Author solution

1. Login at port 6003 with the training member account.
2. Discover `/robots.txt`, `/partners`, and `/static/partner.js`.
3. Identify `/api/v2/member/internal-notices` and the partner header gate enforced by `X-Partner-Client`.
4. Test CORS with an origin ending in `.asterion-partners.local`, such as `https://attacker.asterion-partners.local`.
5. Build `X-Partner-Client` so it starts with `benefits-console` and includes the first hostname label from your attacker origin (for example, `benefits-console-attacker` for `attacker.asterion-partners.local`).
6. Use an attacker-controlled page/request with `credentials: include` and that crafted header. The flawed suffix check reflects the origin and allows credentials, and the partner header check is bypassed because it trusts attacker-controlled origin-derived data.
7. Read `payload.flag` from the JSON response.

The preview page is a clue, not the final exploit. The API requires the authenticated member cookie, accepted origin, and a crafted custom partner header.
