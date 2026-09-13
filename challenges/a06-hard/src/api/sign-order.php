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

$itemId = (string) ($input['item_id'] ?? '');
$priceCents = (int) ($input['price_cents'] ?? 0);
$quantity = (int) ($input['quantity'] ?? 1);

$products = catalog();
if (!isset($products[$itemId])) {
    http_response_code(404);
    echo json_encode(['status' => 'error', 'message' => 'Item not found']);
    exit;
}

// Insecure Design: Generates HMAC token based on client-provided price_cents
// The key is leaked in app.js.map / debug-schema.php
$payload = "{$itemId}:{$priceCents}:{$quantity}";
$orderToken = hash_hmac('sha256', $payload, DEV_SIGNING_SECRET);

echo json_encode([
    'status' => 'success',
    'item_id' => $itemId,
    'price_cents' => $priceCents,
    'quantity' => $quantity,
    'order_token' => $orderToken,
]);
