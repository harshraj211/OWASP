<?php

declare(strict_types=1);

require __DIR__ . "/../includes/bootstrap.php";
requirePost();

$input = $_POST;
if (empty($input)) {
    $raw = (string) @file_get_contents("php://input");
    if ($raw !== "") {
        $json = json_decode($raw, true);
        if (is_array($json)) {
            $input = $json;
        }
    }
}

// 1. Check Gateway Event Header
$eventHeader = (string) ($_SERVER["HTTP_X_GATEWAY_EVENT"] ?? $_SERVER["HTTP_X_EVENT"] ?? "");
if ($eventHeader === "") {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "error" => "Missing gateway event header. Expected header: 'X-Gateway-Event: payment.authorized'",
    ], JSON_PRETTY_PRINT);
    exit;
}

$allowedEvents = ["payment.authorized", "payment.succeeded", "payment.captured", "payment_intent.succeeded", "charge.successful"];
if (!in_array(strtolower($eventHeader), $allowedEvents, true)) {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "error" => "Unsupported gateway event: '" . $eventHeader . "'. Allowed events: " . implode(", ", $allowedEvents),
    ], JSON_PRETTY_PRINT);
    exit;
}

// 2. Validate Payload Parameters
$bookingId = (string) ($input["booking_id"] ?? "");
$transactionId = (string) ($input["transaction_id"] ?? "");
$paymentStatus = strtolower(trim((string) ($input["status"] ?? $input["payment_status"] ?? "")));
$amountCents = (int) ($input["amount_cents"] ?? $input["amount"] ?? 0);

$missing = [];
if ($bookingId === "") $missing[] = "booking_id";
if ($transactionId === "") $missing[] = "transaction_id";
if ($paymentStatus === "") $missing[] = "status (expected 'success', 'approved', or 'settled')";
if ($amountCents <= 0) $missing[] = "amount_cents (expected positive integer in cents)";

if (!empty($missing)) {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "error" => "Missing required gateway payload fields: " . implode(", ", $missing),
        "received_payload" => $input,
    ], JSON_PRETTY_PRINT);
    exit;
}

$record = booking($bookingId);
if ($record === null) {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(404);
    echo json_encode([
        "status" => "error",
        "error" => "Booking record '" . $bookingId . "' not found in active session.",
    ], JSON_PRETTY_PRINT);
    exit;
}

if (!is_array($record["traveler"])) {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "error" => "Traveler details have not been registered for booking '" . $bookingId . "'.",
    ], JSON_PRETTY_PRINT);
    exit;
}

// 3. INSECURE DESIGN FLAW:
// The callback trusts the incoming webhook payload and headers without validating
// a shared HMAC signature (e.g. Stripe-Signature / Webhook Secret) or verifying source IP.
$isSuccessfulStatus = in_array($paymentStatus, ["success", "approved", "authorized", "settled", "paid", "captured"], true);

if ($isSuccessfulStatus) {
    $_SESSION["bookings"][$bookingId]["status"] = "confirmed";
    $_SESSION["bookings"][$bookingId]["payment_status"] = "settled";
    $_SESSION["bookings"][$bookingId]["transaction_id"] = $transactionId;
    $_SESSION["bookings"][$bookingId]["confirmation"] = "AR-" . strtoupper(substr(bin2hex(random_bytes(4)), 0, 7));
    $_SESSION["bookings"][$bookingId]["confirmed_at"] = gmdate(DATE_ATOM);
    $_SESSION["bookings"][$bookingId]["flag"] = getFlag();

    $accept = (string) ($_SERVER["HTTP_ACCEPT"] ?? "");
    $isBrowser = str_contains($accept, "text/html") && !str_contains($accept, "application/json");

    if ($isBrowser) {
        redirectTo("confirmation.php?booking=" . rawurlencode($bookingId));
    }

    header("Content-Type: application/json; charset=utf-8");
    http_response_code(200);
    echo json_encode([
        "status" => "success",
        "event" => $eventHeader,
        "booking_id" => $bookingId,
        "confirmation" => $_SESSION["bookings"][$bookingId]["confirmation"],
        "message" => "Payment successfully settled. Booking confirmed.",
        "redirect_url" => "confirmation.php?booking=" . rawurlencode($bookingId),
    ], JSON_PRETTY_PRINT);
    exit;
}

header("Content-Type: application/json; charset=utf-8");
http_response_code(400);
echo json_encode([
    "status" => "declined",
    "error" => "Gateway reported non-success payment status: '" . $paymentStatus . "'.",
], JSON_PRETTY_PRINT);
