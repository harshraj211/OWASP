<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

$productId = (string) ($_POST['product_id'] ?? '');
$submittedPrice = (string) ($_POST['unit_price'] ?? '');
$products = catalog();
$product = $products[$productId] ?? null;
$submittedPriceCents = submittedPriceToCents($submittedPrice);

if ($product === null || $submittedPriceCents === null) {
    setFlash('error', 'We could not validate that order. Please return to the catalog.');
    redirectHome();
}

// Intentionally vulnerable: checkout trusts the client-provided price instead of catalog price_cents.
$orderTotalCents = $submittedPriceCents;

if ($orderTotalCents > (int) $_SESSION['balance_cents']) {
    setFlash('error', 'Insufficient wallet balance for this order.');
    redirectHome();
}

$_SESSION['balance_cents'] -= $orderTotalCents;
$order = [
    'id' => strtoupper(substr(bin2hex(random_bytes(5)), 0, 8)),
    'product' => $product['name'],
    'charged_cents' => $orderTotalCents,
    'created_at' => gmdate('H:i:s') . ' UTC',
];

if (($product['premium'] ?? false) === true) {
    $order['flag'] = getFlag();
}

array_unshift($_SESSION['orders'], $order);
$_SESSION['orders'] = array_slice($_SESSION['orders'], 0, 5);
setFlash('success', $product['name'] . ' has been fulfilled.');
redirectHome();

