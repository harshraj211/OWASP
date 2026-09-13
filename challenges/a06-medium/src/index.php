<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';
$trip = trip();
$flash = takeFlash();
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>Harborline | Aurora Glass Lodge</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <header class="site-header overlay-header">
        <a class="brand light" href="./"> <img src="assets/logo.webp" alt="RedTeam Hacker Academy" style="height:32px; border-radius:4px; vertical-align:middle; margin-right:8px;"> <span class="brand-mark">H</span><span>Harborline</span></a>
        <nav aria-label="Primary navigation"><a href="#stay">The stay</a><a href="#details">Details</a></nav>
        <form action="reset.php" method="post">
            <?= csrfField() ?>
            <button class="reset-light" type="submit" title="Reset booking session" aria-label="Reset booking session">↻</button>
        </form>
    </header>

    <main>
        <section class="destination-hero" id="stay">
            <div class="hero-shade"></div>
            <div class="hero-copy">
                <p class="eyebrow light-text">Four nights / Northern Norway</p>
                <h1><?= escape($trip['name']) ?></h1>
                <p>Sleep beneath the aurora on the edge of Senja's quietest fjord.</p>
                <form action="start.php" method="post">
                    <?= csrfField() ?>
                    <input type="hidden" name="trip_id" value="<?= escape($trip['id']) ?>">
                    <button class="primary-button light-button" type="submit">Reserve your stay</button>
                </form>
            </div>
            <div class="hero-facts">
                <div><span>From</span><strong><?= escape(money($trip['price_cents'])) ?></strong></div>
                <div><span>Dates</span><strong>Nov 18-22</strong></div>
                <div><span>Guests</span><strong>1 guest</strong></div>
            </div>
        </section>

        <?php if ($flash !== null): ?>
            <div class="notice notice-<?= escape($flash['type']) ?>" role="status"><?= escape($flash['message']) ?></div>
        <?php endif; ?>

        <section class="experience" id="details">
            <div class="section-intro">
                <p class="eyebrow">The experience</p>
                <h2>Wild horizons.<br>Considered comfort.</h2>
            </div>
            <div class="experience-copy">
                <p>A private glass-roof lodge, daily breakfast, guided fjord crossing, and two evenings with a local aurora guide.</p>
                <dl>
                    <div><dt>Stay</dt><dd>4 nights</dd></div>
                    <div><dt>Arrival</dt><dd>Tromsø transfer included</dd></div>
                    <div><dt>Cancellation</dt><dd>Free for 48 hours</dd></div>
                </dl>
            </div>
        </section>
    </main>

    <footer><span>Harborline Travel Co.</span><span>Curated northern stays</span></footer>
</body>
</html>

