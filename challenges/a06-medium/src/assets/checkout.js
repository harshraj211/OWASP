const paymentForm = document.querySelector('#payment-form');

if (paymentForm) {
    // Gateway integration metadata
    window.HarborlineGateway = {
        provider: 'nordicpay-v2',
        handler: '/checkout/gateway-callback.php',
        version: '2.4.0'
    };

    paymentForm.addEventListener('submit', () => {
        const button = paymentForm.querySelector('button[type="submit"]');
        if (button) {
            button.disabled = true;
            const span = button.querySelector('span');
            if (span) {
                span.textContent = 'Authorizing payment...';
            }
        }
    });
}

