<?php

declare(strict_types=1);

require_once __DIR__ . '/../includes/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

$input = $_POST;
if (empty($input)) {
    $raw = (string) @file_get_contents('php://input');
    if ($raw !== '') {
        $json = json_decode($raw, true);
        if (is_array($json)) {
            $input = $json;
        }
    }
}

$itemId = (string) ($input['item_id'] ?? '');
$priceCents = (int) ($input['price_cents'] ?? 0);
$quantity = (int) ($input['quantity'] ?? 1);
$orderToken = (string) ($input['order_token'] ?? '');

$catalog = catalog();
$item = $catalog[$itemId] ?? null;

if ($item === null || $quantity < 1) {
    setFlash('error', 'Unable to process order. Invalid item or quantity.');
    redirectHome();
}

$tier = getUserTier();

// Check 1: Tier restriction (bypassable via cookie HMAC forgery)
if (($item['premium'] ?? false) === true && $tier !== 'sovereign_vip') {
    setFlash('error', 'Restricted item! Purchase requires Sovereign VIP membership tier.');
    redirectHome();
}

// Check 2: Order token signature verification (bypassable using leaked DEV_SIGNING_SECRET)
$expectedToken = hash_hmac('sha256', "{$itemId}:{$priceCents}:{$quantity}", DEV_SIGNING_SECRET);
if ($orderToken === '' || !hash_equals($expectedToken, $orderToken)) {
    setFlash('error', 'Invalid order security token signature.');
    redirectHome();
}

$userId = (string) ($_SESSION['user_id'] ?? '');
$user = getUserData($userId);

$orderTotal = $priceCents * $quantity;

// Check 3: Wallet balance check (bypassable by stacking coupon race condition + multiplier)
if ($orderTotal > (int) ($user['balance_cents'] ?? 0)) {
    setFlash('error', 'Insufficient wallet balance for this purchase. Balance: ' . money((int) $user['balance_cents']) . ', Required: ' . money($orderTotal));
    redirectHome();
}

// Deduct balance
$user['balance_cents'] -= $orderTotal;
saveUserData($userId, $user);

// Create order
$orderId = 'ORD-' . strtoupper(substr(bin2hex(random_bytes(4)), 0, 8));
$flag = null;
if (($item['premium'] ?? false) === true) {
    $flag = getFlag();
}

$orderRecord = [
    'id' => $orderId,
    'user_id' => $userId,
    'item_id' => $itemId,
    'item_name' => $item['name'],
    'charged_cents' => $orderTotal,
    'flag' => $flag,
    'created_at' => gmdate('c'),
];
saveOrder($userId, $orderRecord);

setFlash('success', "Order {$orderId} fulfilled successfully for {$item['name']}.");
redirectHome();
