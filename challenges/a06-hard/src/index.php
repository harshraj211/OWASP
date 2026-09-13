<?php

declare(strict_types=1);

require_once __DIR__ . '/includes/bootstrap.php';

$userId = (string) ($_SESSION['user_id'] ?? '');
$user = getUserData($userId);

$tier = getUserTier();
$products = catalog();
$flash = takeFlash();
$orders = getOrders($userId);
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Apex Sovereign Vault | Exclusive Reserve</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <header class="site-header">
        <a class="brand" href="./"> <img src="assets/logo.webp" alt="RedTeam Hacker Academy" style="height:32px; border-radius:4px; vertical-align:middle; margin-right:8px;"> 
            <span class="brand-mark">A</span>
            <span>Apex Sovereign Vault</span>
        </a>
        <div class="header-actions">
            <span class="tier-pill <?= $tier === 'sovereign_vip' ? 'tier-vip' : '' ?>">
                Tier: <?= escape(strtoupper(str_replace('_', ' ', $tier))) ?>
            </span>
            <div class="wallet-badge">
                <span class="wallet-label">Reserve Balance</span>
                <span class="wallet-amount"><?= escape(money((int) ($user['balance_cents'] ?? 0))) ?></span>
            </div>
            <form action="reset.php" method="post">
                <button class="btn-icon" type="submit" title="Reset Session" aria-label="Reset Session">↻</button>
            </form>
        </div>
    </header>

    <main>
        <section class="hero-banner">
            <div class="hero-copy">
                <h1>High-Net-Worth Asset Reserve</h1>
                <p>Access minted assets, private club passes, and sovereign vault credentials. Redeem promotional vouchers to fund your reserve balance.</p>
            </div>
            <div class="coupon-box">
                <h3>Redeem Voucher</h3>
                <form id="coupon-form" class="coupon-form">
                    <input type="text" id="coupon-code" placeholder="e.g. WELCOME50" required>
                    <button type="submit">Apply</button>
                </form>
            </div>
        </section>

        <?php if ($flash !== null): ?>
            <div class="notice notice-<?= escape($flash['type']) ?>">
                <span><?= escape($flash['message']) ?></span>
                <button type="button" class="notice-close">×</button>
            </div>
        <?php endif; ?>

        <section class="catalog-section">
            <div class="section-header">
                <h2>Vault Catalog</h2>
                <span style="color: var(--text-secondary); font-size: 0.9rem;">Direct reserve ledger settlement</span>
            </div>

            <div class="catalog-grid">
                <?php foreach ($products as $id => $product): ?>
                    <article class="card <?= ($product['premium'] ?? false) ? 'card-premium' : '' ?>">
                        <div>
                            <span class="card-badge <?= ($product['premium'] ?? false) ? 'badge-restricted' : 'badge-standard' ?>">
                                <?= ($product['premium'] ?? false) ? 'Sovereign VIP Only' : 'Open Catalog' ?>
                            </span>
                            <h3 class="card-title"><?= escape($product['name']) ?></h3>
                            <p class="card-desc"><?= escape($product['description']) ?></p>
                        </div>
                        <div class="card-action">
                            <span class="card-price"><?= escape(money($product['price_cents'])) ?></span>
                            <form class="purchase-form" action="checkout/purchase.php" method="post">
                                <?= csrfField() ?>
                                <input type="hidden" name="item_id" value="<?= escape($id) ?>">
                                <input type="hidden" name="price_cents" value="<?= (int) $product['price_cents'] ?>">
                                <input type="hidden" name="quantity" value="1">
                                <input type="hidden" name="order_token" value="">
                                <button type="submit" class="btn-primary">Acquire</button>
                            </form>
                        </div>
                    </article>
                <?php endforeach; ?>
            </div>
        </section>

        <section class="orders-section">
            <div class="section-header">
                <h2>Ledger Transactions</h2>
                <span style="color: var(--text-secondary); font-size: 0.9rem;"><?= count($orders) ?> fulfilled</span>
            </div>

            <?php if (empty($orders)): ?>
                <div style="text-align: center; padding: 3rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text-muted);">
                    No completed vault orders in this session.
                </div>
            <?php else: ?>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Transaction</th>
                                <th>Item</th>
                                <th>Amount Charged</th>
                                <th>Timestamp</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($orders as $order): ?>
                                <tr>
                                    <td><strong><?= escape($order['id']) ?></strong></td>
                                    <td><?= escape($order['item_name']) ?></td>
                                    <td><?= escape(money((int) $order['charged_cents'])) ?></td>
                                    <td><?= escape($order['created_at']) ?></td>
                                    <td><span style="color: var(--success); font-weight: 700;">Fulfilled</span></td>
                                </tr>
                                <?php if (!empty($order['flag'])): ?>
                                    <tr>
                                        <td colspan="5">
                                            <div class="flag-box">
                                                <span>Sovereign Reserve Access Token Recovered</span>
                                                <code><?= escape($order['flag']) ?></code>
                                            </div>
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
        <span>Apex Sovereign Vault Reserve Ltd.</span>
        <span>Secure Enclave Infrastructure v2.4.1</span>
    </footer>

    <script src="assets/app.js"></script>
</body>
</html>
