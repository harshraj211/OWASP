<?php

declare(strict_types=1);

require __DIR__ . '/includes/bootstrap.php';
requirePost();

if (!validCsrf()) {
    http_response_code(400);
    exit('Invalid request');
}

$_SESSION = [];
session_regenerate_id(true);
setFlash('success', 'Your booking session has been reset.');
redirectTo('./');

