<?php

declare(strict_types=1);

require_once __DIR__ . '/../includes/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');

echo json_encode([
    'service' => 'Apex Vault Internal API Gateway (Staging Build v2.4.1-rc3)',
    'environment' => 'staging-debug',
    'endpoints' => [
        [
            'path' => '/api/redeem.php',
            'method' => 'POST',
            'description' => 'Redeem promotional coupons for store wallet credit',
            'params' => [
                'code' => ['type' => 'string', 'required' => true, 'example' => 'WELCOME50'],
                'multiplier' => ['type' => 'integer', 'required' => false, 'default' => 1, 'notes' => 'INTERNAL QA USE ONLY: Multiplies coupon credit value up to 10x for automated test account funding.'],
            ],
        ],
        [
            'path' => '/api/sign-order.php',
            'method' => 'POST',
            'description' => 'Sign purchase order parameters with HMAC-SHA256',
            'params' => [
                'item_id' => ['type' => 'string', 'required' => true],
                'price_cents' => ['type' => 'integer', 'required' => true],
                'quantity' => ['type' => 'integer', 'required' => true],
            ],
            'signing_algorithm' => 'HMAC-SHA256',
            'signing_format' => '{item_id}:{price_cents}:{quantity}',
            'dev_secret_reference' => 'apex_dev_sec_994821',
        ],
        [
            'path' => '/checkout/purchase.php',
            'method' => 'POST',
            'description' => 'Finalize vault purchase',
            'requirements' => [
                'tier' => 'Client cookie apex_member_tier must contain tier sovereign_vip for restricted items.',
                'balance' => 'User wallet balance_cents >= order total.',
                'order_token' => 'Valid HMAC signature matching item_id, charged price_cents, and quantity.',
            ],
        ],
    ],
    'developer_notes' => [
        'Security Review Note #1: Remove multiplier param before production cutover.',
        'Security Review Note #2: Move apex_dev_sec_994821 out of client-accessible bundles and cookie HMAC signatures.',
    ],
], JSON_PRETTY_PRINT);
