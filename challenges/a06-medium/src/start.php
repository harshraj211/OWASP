<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';
requirePost();

if (!validCsrf() || ($_POST['trip_id'] ?? '') !== trip()['id']) {
    http_response_code(400);
    exit('Invalid booking request');
}

$bookingId = 'HL-' . strtoupper(substr(bin2hex(random_bytes(4)), 0, 6));
$_SESSION['bookings'][$bookingId] = [
    'id' => $bookingId,
    'trip' => trip(),
    'status' => 'draft',
    'payment_status' => 'unpaid',
    'traveler' => null,
    'created_at' => gmdate(DATE_ATOM),
];

redirectTo('checkout/details.php?booking=' . rawurlencode($bookingId));

