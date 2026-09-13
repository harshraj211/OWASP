<?php

declare(strict_types=1);

require_once __DIR__ . '/../includes/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');

$userId = (string) ($_SESSION['user_id'] ?? '');
$user = getUserData($userId);
$tier = getUserTier();

echo json_encode([
    'status' => 'success',
    'user_id' => $userId,
    'balance_cents' => (int) ($user['balance_cents'] ?? 0),
    'balance_display' => money((int) ($user['balance_cents'] ?? 0)),
    'tier' => $tier,
    'is_vip' => ($tier === 'sovereign_vip'),
    'redemptions' => $user['redemptions'] ?? [],
]);
