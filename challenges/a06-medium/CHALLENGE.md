# A06:2025 - Insecure Design (Medium)

## Payment Workflow Bypass

Harborline offers a limited Arctic lodge package through its online booking flow. Reservations should be confirmed only after the external card processor authorizes payment.

Complete a reservation for the **Aurora Glass Lodge** without making a successful payment and recover the confirmation code issued with the booking.

- Category: A06:2025 - Insecure Design
- Difficulty: Medium
- Estimated time: 25-40 minutes
- Flag format: `CTF{...}`

Only interact with the challenge through its web interface and HTTP requests.

