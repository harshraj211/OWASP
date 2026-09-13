<?php

declare(strict_types=1);

require_once __DIR__ . '/includes/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

$userId = (string) ($_SESSION['user_id'] ?? '');
if ($userId !== '') {
    resetUserData($userId);
}

if (session_status() !== PHP_SESSION_ACTIVE) {
    @session_start();
}
$_SESSION = [];
session_regenerate_id(true);

// Reset cookie
$newUserId = 'usr_' . substr(bin2hex(random_bytes(6)), 0, 10);
$_SESSION['user_id'] = $newUserId;
$_SESSION['csrf_token'] = bin2hex(random_bytes(24));

$tierPayload = json_encode([
    'user_id' => $newUserId,
    'tier' => 'standard',
    'issued_at' => time(),
]);
$tierB64 = base64_encode($tierPayload);
$sig = hash_hmac('sha256', $tierB64, DEV_SIGNING_SECRET);
setcookie('apex_member_tier', $tierB64 . '.' . $sig, [
    'httponly' => false,
    'samesite' => 'Lax',
    'path' => '/',
]);

setFlash('success', 'Lab session has been reset. Wallet balance restored to starting funds.');
redirectHome();
