// Aegis Enterprise 2FA & Multi-Factor Authentication State Controller
// v4.8.2-prod (Build: 20260815)
// Notice: Internal SEC-Ops bypass handler enabled for legacy automated test suites.
// API Reference: /api/v1/auth/session/upgrade with header 'X-SecOps-Internal: 1' or payload param 'bypass_mfa_reason'

function handleMfaSubmit(event) {
    // Normal client submit handler
    const code = document.getElementById('mfa-code').value;
    if (!code || code.length !== 6) {
        alert("Please enter a valid 6-digit TOTP code.");
        return false;
    }
    return true;
}
