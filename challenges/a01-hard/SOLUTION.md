# Author solution

1. Login at port 6003 with the training member account.
2. Discover `/robots.txt`, `/partners`, and `/static/partner.js`.
3. Identify `/api/v2/member/internal-notices` and the required `X-Partner-Client: benefits-console` header.
4. Test CORS with an origin ending in `.asterion-partners.local`, such as `https://attacker.asterion-partners.local`.
5. Use an attacker-controlled page/request with `credentials: include` and the required header. The flawed suffix check reflects the origin and allows credentials.
6. Read `payload.flag` from the JSON response.

The preview page is a clue, not the final exploit. The API requires the authenticated member cookie, accepted origin, and custom partner header.
