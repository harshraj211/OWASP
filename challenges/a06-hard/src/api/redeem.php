<?php

declare(strict_types=1);

require_once __DIR__ . '/../includes/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method Not Allowed']);
    exit;
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

$code = strtoupper(trim((string) ($input['code'] ?? '')));
$userId = (string) ($_SESSION['user_id'] ?? '');

// Flaw 2: Hidden legacy developer test parameter 'multiplier' (or 'coupon_multiplier')
$multiplier = 1;
if (isset($input['multiplier']) || isset($input['coupon_multiplier'])) {
    $rawMult = (int) ($input['multiplier'] ?? $input['coupon_multiplier'] ?? 1);
    $multiplier = max(1, min($rawMult, 10)); // Capped between 1 and 10
}

$availableCoupons = coupons();
$coupon = $availableCoupons[$code] ?? null;

if ($coupon === null || $userId === '') {
    http_response_code(404);
    echo json_encode(['status' => 'error', 'message' => 'Invalid or expired coupon voucher code']);
    exit;
}

// Flaw 1: Non-atomic Check-Then-Apply Race Condition
$userData = getUserData($userId);
$redemptions = $userData['redemptions'] ?? [];

if (in_array($code, $redemptions, true)) {
    http_response_code(409);
    echo json_encode([
        'status' => 'error',
        'message' => "Coupon {$code} has already been redeemed for this account.",
    ]);
    exit;
}

// Artificial processing delay (reproduces check-then-apply race condition window)
usleep(120000); // 120ms

$creditAmount = (int) $coupon['amount_cents'] * $multiplier;

// Apply credit and record redemption
$freshData = getUserData($userId);
$freshData['balance_cents'] = (int) ($freshData['balance_cents'] ?? 0) + $creditAmount;
if (!in_array($code, $freshData['redemptions'], true)) {
    $freshData['redemptions'][] = $code;
}
saveUserData($userId, $freshData);

http_response_code(200);
echo json_encode([
    'status' => 'success',
    'message' => "Coupon {$code} redeemed successfully.",
    'credited_cents' => $creditAmount,
    'credited_display' => money($creditAmount),
    'new_balance_cents' => $freshData['balance_cents'],
    'new_balance_display' => money($freshData['balance_cents']),
    'multiplier_applied' => $multiplier,
]);
