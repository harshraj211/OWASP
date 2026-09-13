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
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Review booking | Harborline</title><link rel="stylesheet" href="../assets/styles.css"></head>
<body class="checkout-body">
    <header class="site-header"><a class="brand" href="../"><span class="brand-mark">H</span><span>Harborline</span></a><span class="secure-label">Booking <?= escape($bookingId) ?></span></header>
    <main class="checkout-shell">
        <?= checkoutSteps(2) ?>
        <div class="checkout-layout">
            <section class="checkout-main">
                <p class="eyebrow">Step 2 of 4</p><h1>Review your booking</h1><p class="lede">Confirm your traveler and itinerary information before payment.</p>
                <div class="review-block"><div><span>Traveler</span><a href="details.php?booking=<?= rawurlencode($bookingId) ?>">Edit</a></div><h2><?= escape($record['traveler']['full_name']) ?></h2><p><?= escape($record['traveler']['email']) ?><br><?= escape($record['traveler']['country']) ?> · Passport ending <?= escape(substr($record['traveler']['passport'], -4)) ?></p></div>
                <form action="payment.php" method="get"><input type="hidden" name="booking" value="<?= escape($bookingId) ?>"><button class="primary-button" type="submit">Continue to payment</button></form>
            </section>
            <aside class="booking-summary"><?php require __DIR__ . '/summary.php'; ?></aside>
        </div>
    </main>
</body></html>

