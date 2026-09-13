// Aegis Enterprise 2FA State Controller
// Build: 20260815-prod

function handleMfaSubmit(event) {
    const code = document.getElementById('mfa-code');
    if (code && (!code.value || code.value.length !== 6)) {
        alert("Please enter a valid 6-digit TOTP verification token.");
        return false;
    }
    return true;
}
