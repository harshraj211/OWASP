<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

$_SESSION = [];
session_regenerate_id(true);
$_SESSION['balance_cents'] = STARTING_BALANCE_CENTS;
$_SESSION['orders'] = [];
setFlash('success', 'Store session reset. Your wallet is back to its starting balance.');
redirectHome();

