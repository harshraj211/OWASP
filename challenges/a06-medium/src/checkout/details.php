<?php

declare(strict_types=1);

require __DIR__ . '/../includes/bootstrap.php';
$bookingId = (string) ($_GET['booking'] ?? '');
$record = booking($bookingId);
if ($record === null) {
    redirectTo('../');
}
$traveler = is_array($record['traveler']) ? $record['traveler'] : [];
$flash = takeFlash();
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Traveler details | Harborline</title><link rel="stylesheet" href="../assets/styles.css"></head>
<body class="checkout-body">
    <header class="site-header"><a class="brand" href="../"><span class="brand-mark">H</span><span>Harborline</span></a><span class="secure-label">Booking <?= escape($bookingId) ?></span></header>
    <main class="checkout-shell">
        <?= checkoutSteps(1) ?>
        <?php if ($flash !== null): ?><div class="notice notice-<?= escape($flash['type']) ?>" role="status"><?= escape($flash['message']) ?></div><?php endif; ?>
        <div class="checkout-layout">
            <section class="checkout-main">
                <p class="eyebrow">Step 1 of 4</p><h1>Traveler details</h1><p class="lede">Enter the information exactly as it appears on your travel document.</p>
                <form class="details-form" action="save-details.php" method="post">
                    <?= csrfField() ?><input type="hidden" name="booking_id" value="<?= escape($bookingId) ?>">
                    <label>Full name<input name="full_name" autocomplete="name" value="<?= escape((string) ($traveler['full_name'] ?? '')) ?>" required maxlength="80"></label>
                    <label>Email address<input name="email" type="email" autocomplete="email" value="<?= escape((string) ($traveler['email'] ?? '')) ?>" required maxlength="120"></label>
                    <div class="field-row">
                        <label>Country<input name="country" value="<?= escape((string) ($traveler['country'] ?? '')) ?>" required maxlength="60"></label>
                        <label>Passport number<input name="passport" value="<?= escape((string) ($traveler['passport'] ?? '')) ?>" required pattern="[A-Za-z0-9-]{5,20}" maxlength="20"></label>
                    </div>
                    <button class="primary-button" type="submit">Continue to review</button>
                </form>
            </section>
            <aside class="booking-summary"><?php require __DIR__ . '/summary.php'; ?></aside>
        </div>
    </main>
</body></html>

