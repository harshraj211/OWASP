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

$bookingId = (string) ($input["booking_id"] ?? "");
$record = booking($bookingId);

if (!validCsrf() || $record === null || !is_array($record["traveler"])) {
    http_response_code(400);
    exit("Invalid payment request");
}

$cardNumber = preg_replace("/\D+/", "", (string) ($input["card_number"] ?? ""));
$expiry = (string) ($input["expiry"] ?? "");
$cvv = (string) ($input["cvv"] ?? "");

if ($cardNumber !== "" && (!preg_match("/^\d{13,19}$/", $cardNumber) || !preg_match("/^(0[1-9]|1[0-2])\/\d{2}$/", $expiry) || !preg_match("/^\d{3,4}$/", $cvv))) {
    setFlash("error", "Check your card details and try again.");
    redirectTo("payment.php?booking=" . rawurlencode($bookingId));
}

// Generate transaction reference for this attempt
$transactionId = "TXN_" . strtolower(substr(bin2hex(random_bytes(6)), 0, 10));
$_SESSION["bookings"][$bookingId]["payment_status"] = "declined";
$_SESSION["bookings"][$bookingId]["last_transaction_id"] = $transactionId;
$_SESSION["bookings"][$bookingId]["payment_attempted_at"] = gmdate(DATE_ATOM);

// Check if request is AJAX/API client expecting JSON
$accept = (string) ($_SERVER["HTTP_ACCEPT"] ?? "");
$isJson = str_contains($accept, "application/json") || isset($_SERVER["HTTP_X_REQUESTED_WITH"]);

if ($isJson) {
    header("Content-Type: application/json; charset=utf-8");
    http_response_code(402);
    echo json_encode([
        "status" => "declined",
        "error" => "Card authorization declined: Insufficient funds (ERR_DECLINED_042)",
        "booking_id" => $bookingId,
        "transaction_id" => $transactionId,
        "amount_cents" => $record["trip"]["price_cents"],
        "gateway_provider" => "nordicpay-v2",
        "callback_handler" => "/checkout/gateway-callback.php",
    ]);
    exit;
}

setFlash("error", "Payment gateway declined this authorization (ERR_CARD_DECLINED_INSUFFICIENT_FUNDS). Transaction: " . $transactionId . " [Handler: /checkout/gateway-callback.php]");
redirectTo("payment.php?booking=" . rawurlencode($bookingId));
