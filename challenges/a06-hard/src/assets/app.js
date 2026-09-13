/**
 * Apex Sovereign Vault - Client Application v2.4.1
 * (c) Apex Luxury Collectibles Ltd.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Dismiss notice
    document.querySelectorAll('.notice-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.notice').remove();
        });
    });

    // Coupon redeem form handler
    const couponForm = document.getElementById('coupon-form');
    if (couponForm) {
        couponForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('coupon-code');
            const code = input.value.trim();
            if (!code) return;

            const btn = couponForm.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Applying...';

            try {
                const res = await fetch('api/redeem.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                    },
                    body: new URLSearchParams({ code }),
                });
                const data = await res.json();
                if (res.ok && data.status === 'success') {
                    window.location.reload();
                } else {
                    alert(data.message || 'Coupon could not be applied.');
                }
            } catch (err) {
                alert('Network error while redeeming coupon.');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Apply Coupon';
            }
        });
    }

    // Purchase token signing
    document.querySelectorAll('.purchase-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            const tokenInput = form.querySelector('input[name="order_token"]');
            if (tokenInput && tokenInput.value === '') {
                e.preventDefault();
                const itemId = form.querySelector('input[name="item_id"]').value;
                const priceCents = form.querySelector('input[name="price_cents"]').value;
                const quantity = form.querySelector('input[name="quantity"]')?.value || 1;

                try {
                    const res = await fetch('api/sign-order.php', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: new URLSearchParams({ item_id: itemId, price_cents: priceCents, quantity: quantity }),
                    });
                    const data = await res.json();
                    if (data.order_token) {
                        tokenInput.value = data.order_token;
                        form.submit();
                    }
                } catch (err) {
                    form.submit();
                }
            }
        });
    });
});
//# sourceMappingURL=app.js.map
