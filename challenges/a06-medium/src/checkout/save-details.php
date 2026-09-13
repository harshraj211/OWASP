<?php

declare(strict_types=1);

require __DIR__ . '/../includes/bootstrap.php';
requirePost();
$bookingId = (string) ($_POST['booking_id'] ?? '');
$record = booking($bookingId);

if (!validCsrf() || $record === null) {
    http_response_code(400);
    exit('Invalid booking request');
}

$fullName = trim((string) ($_POST['full_name'] ?? ''));
$email = trim((string) ($_POST['email'] ?? ''));
$country = trim((string) ($_POST['country'] ?? ''));
$passport = trim((string) ($_POST['passport'] ?? ''));

if ($fullName === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || $country === '' || !preg_match('/^[A-Za-z0-9-]{5,20}$/', $passport)) {
    setFlash('error', 'Check the traveler information and try again.');
    redirectTo('details.php?booking=' . rawurlencode($bookingId));
}

$_SESSION['bookings'][$bookingId]['traveler'] = [
    'full_name' => $fullName,
    'email' => $email,
    'country' => $country,
    'passport' => strtoupper($passport),
];
$_SESSION['bookings'][$bookingId]['status'] = 'details_complete';
redirectTo('review.php?booking=' . rawurlencode($bookingId));

