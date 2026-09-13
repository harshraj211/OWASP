<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';

$products = catalog();
$flash = takeFlash();
$orders = $_SESSION['orders'];
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>Northstar Market</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <header class="site-header">
        <a class="brand" href="./" aria-label="Northstar Market home"> <img src="assets/logo.webp" alt="RedTeam Hacker Academy" style="height:32px; border-radius:4px; vertical-align:middle; margin-right:8px;"> 
            <span class="brand-mark" aria-hidden="true">N</span>
            <span>Northstar Market</span>
        </a>
        <div class="header-actions">
            <div class="wallet" aria-label="Wallet balance">
                <span class="wallet-label">Wallet</span>
                <strong><?= escape(money((int) $_SESSION['balance_cents'])) ?></strong>
            </div>
            <form action="reset.php" method="post">
                <button class="icon-button" type="submit" title="Reset store session" aria-label="Reset store session">
                    <span aria-hidden="true">↻</span>
                </button>
            </form>
        </div>
    </header>

    <main>
        <section class="hero" aria-labelledby="hero-title">
            <div class="hero-image" role="img" aria-label="Products from the Northstar collection"></div>
            <div class="hero-copy">
                <p class="kicker">New season / Everyday essentials</p>
                <h1 id="hero-title">Northstar Market</h1>
                <p>Well-made objects for work, weekends, and wherever you go next.</p>
                <a class="primary-link" href="#catalog">Shop collection <span aria-hidden="true">↓</span></a>
            </div>
        </section>

        <?php if ($flash !== null): ?>
            <div class="notice notice-<?= escape($flash['type']) ?>" role="status">
                <span><?= escape($flash['message']) ?></span>
                <button type="button" class="notice-close" aria-label="Dismiss notification">×</button>
            </div>
        <?php endif; ?>

        <section class="catalog-section" id="catalog" aria-labelledby="catalog-title">
            <div class="section-heading">
                <div>
                    <p class="kicker">Current inventory</p>
                    <h2 id="catalog-title">Field catalog</h2>
                </div>
                <p>Orders are charged directly to your store wallet.</p>
            </div>

            <div class="product-grid">
                <?php foreach ($products as $id => $product): ?>
                    <article class="product-card <?= ($product['premium'] ?? false) ? 'product-premium' : '' ?>">
                        <div class="product-visual visual-<?= escape($product['visual']) ?>">
                            <span><?= escape($product['eyebrow']) ?></span>
                        </div>
                        <div class="product-content">
                            <div class="product-title-row">
                                <h3><?= escape($product['name']) ?></h3>
                                <?php if (($product['premium'] ?? false) === true): ?>
                                    <span class="restricted">Restricted</span>
                                <?php endif; ?>
                            </div>
                            <p><?= escape($product['description']) ?></p>
                            <div class="product-purchase">
                                <strong><?= escape(money($product['price_cents'])) ?></strong>
                                <form action="purchase.php" method="post">
                                    <input type="hidden" name="product_id" value="<?= escape($id) ?>">
                                    <input type="hidden" name="unit_price" value="<?= number_format($product['price_cents'] / 100, 2, '.', '') ?>">
                                    <button type="submit">Purchase</button>
                                </form>
                            </div>
                        </div>
                    </article>
                <?php endforeach; ?>
            </div>
        </section>

        <section class="orders-section" aria-labelledby="orders-title">
            <div class="section-heading compact">
                <div>
                    <p class="kicker">Account activity</p>
                    <h2 id="orders-title">Recent orders</h2>
                </div>
                <span class="order-count"><?= count($orders) ?> / 5</span>
            </div>

            <?php if ($orders === []): ?>
                <div class="empty-state">
                    <span class="empty-icon" aria-hidden="true">□</span>
                    <p>No completed orders in this session.</p>
                </div>
            <?php else: ?>
                <div class="orders-table-wrap">
                    <table>
                        <thead>
                            <tr><th>Order</th><th>Item</th><th>Charged</th><th>Time</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                        <?php foreach ($orders as $order): ?>
                            <tr>
                                <td data-label="Order">#<?= escape($order['id']) ?></td>
                                <td data-label="Item"><?= escape($order['product']) ?></td>
                                <td data-label="Charged"><?= escape(money((int) $order['charged_cents'])) ?></td>
                                <td data-label="Time"><?= escape($order['created_at']) ?></td>
                                <td data-label="Status"><span class="fulfilled">Fulfilled</span></td>
                            </tr>
                            <?php if (isset($order['flag'])): ?>
                                <tr class="flag-row">
                                    <td colspan="5">
                                        <span>Restricted shipment access code</span>
                                        <code><?= escape($order['flag']) ?></code>
                                    </td>
                                </tr>
                            <?php endif; ?>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </section>
    </main>

    <footer>
        <span>Northstar Market Co.</span>
        <span>Shipping worldwide</span>
    </footer>
    <script src="assets/app.js"></script>
</body>
</html>
