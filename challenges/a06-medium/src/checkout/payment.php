<?php

declare(strict_types=1);

require __DIR__ . '/../includes/bootstrap.php';
$bookingId = (string) ($_GET['booking'] ?? '');
$record = booking($bookingId);
if ($record === null) {
    redirectTo('../');
}
if (!is_array($record['traveler'])) {
    redirectTo('details.php?booking=' . rawurlencode($bookingId));
}
$flash = takeFlash();
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Payment | Harborline</title><link rel="stylesheet" href="../assets/styles.css"></head>
<body class="checkout-body">
    <header class="site-header"><a class="brand" href="../"><span class="brand-mark">H</span><span>Harborline</span></a><span class="secure-label">Booking <?= escape($bookingId) ?></span></header>
    <main class="checkout-shell">
        <?= checkoutSteps(3) ?>
        <?php if ($flash !== null): ?><div class="notice notice-<?= escape($flash['type']) ?>" role="status"><?= escape($flash['message']) ?></div><?php endif; ?>
        <div class="checkout-layout">
            <section class="checkout-main">
                <p class="eyebrow">Step 3 of 4</p><h1>Secure payment</h1><p class="lede">Your reservation is held for ten minutes while payment is authorized with our partner gateway.</p>
                <form id="payment-form" class="payment-form" action="process-payment.php" method="post">
                    <?= csrfField() ?><input type="hidden" name="booking_id" value="<?= escape($bookingId) ?>">
                    <input type="hidden" name="payment_gateway" value="harborline-pay-v2">
                    <input type="hidden" name="payment_status" value="declined">
                    <label>Name on card<input name="card_name" autocomplete="cc-name" placeholder="Alex Morgan" required></label>
                    <label>Card number<input name="card_number" inputmode="numeric" autocomplete="cc-number" placeholder="4242 4242 4242 4242" required maxlength="23"></label>
                    <div class="field-row"><label>Expiration<input name="expiry" autocomplete="cc-exp" placeholder="MM/YY" required maxlength="5"></label><label>Security code<input name="cvv" type="password" inputmode="numeric" autocomplete="cc-csc" placeholder="CVV" required maxlength="4"></label></div>
                    <button class="primary-button pay-button" type="submit"><span>Authorize payment</span><strong><?= escape(money($record['trip']['price_cents'])) ?></strong></button>
                </form>
                <p class="payment-note">Card details are encrypted and authorized via Harborline's external gateway. Sensitive card data is not retained.</p>
            </section>
            <aside class="booking-summary"><?php require __DIR__ . '/summary.php'; ?></aside>
        </div>
    </main>
    <script src="../assets/checkout.js"></script>
</body></html>

