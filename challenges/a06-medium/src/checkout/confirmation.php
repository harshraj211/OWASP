<?php

declare(strict_types=1);

require __DIR__ . '/../includes/bootstrap.php';
$bookingId = (string) ($_GET['booking'] ?? '');
$record = booking($bookingId);
if ($record === null || $record['status'] !== 'confirmed') {
    redirectTo('../');
}
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Booking confirmed | Harborline</title><link rel="stylesheet" href="../assets/styles.css"></head>
<body class="checkout-body">
    <header class="site-header"><a class="brand" href="../"><span class="brand-mark">H</span><span>Harborline</span></a><span class="secure-label">Booking <?= escape($bookingId) ?></span></header>
    <main class="checkout-shell confirmation-shell">
        <?= checkoutSteps(4) ?>
        <section class="confirmation-panel">
            <div class="confirmation-mark" aria-hidden="true">✓</div>
            <p class="eyebrow">Reservation confirmed</p>
            <h1>Your place beneath the aurora is secured.</h1>
            <p>We sent the itinerary to <?= escape($record['traveler']['email']) ?>.</p>
            <div class="confirmation-details"><div><span>Confirmation</span><strong><?= escape($record['confirmation']) ?></strong></div><div><span>Payment status</span><strong class="<?= in_array(strtolower((string) ($record['payment_status'] ?? '')), ['authorized', 'approved', 'success', 'completed', 'paid'], true) ? 'payment-authorized' : 'payment-unpaid' ?>"><?= escape(ucfirst((string) ($record['payment_status'] ?? 'Bypassed'))) ?></strong></div><div><span>Total</span><strong><?= escape(money($record['trip']['price_cents'])) ?></strong></div></div>
            <div class="flag-box"><span>Expedition access code</span><code><?= escape($record['flag']) ?></code></div>
            <a class="secondary-link" href="../">Return to Harborline</a>
        </section>
    </main>
</body></html>

