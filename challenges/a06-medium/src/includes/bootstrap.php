<?php

declare(strict_types=1);

session_name('harborline_booking');
session_set_cookie_params([
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_start();

if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(24));
}

if (!isset($_SESSION['bookings']) || !is_array($_SESSION['bookings'])) {
    $_SESSION['bookings'] = [];
}

function trip(): array
{
    return [
        'id' => 'aurora-glass-lodge',
        'name' => 'Aurora Glass Lodge',
        'location' => 'Senja, Northern Norway',
        'dates' => 'November 18-22, 2026',
        'nights' => 4,
        'guests' => 1,
        'price_cents' => 245000,
    ];
}

function escape(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function money(int $cents): string
{
    return '$' . number_format($cents / 100, 2);
}

function csrfField(): string
{
    return '<input type="hidden" name="csrf_token" value="' . escape((string) $_SESSION['csrf_token']) . '">';
}

function validCsrf(): bool
{
    $submitted = (string) ($_POST['csrf_token'] ?? '');
    if ($submitted === '') {
        $raw = (string) @file_get_contents('php://input');
        if ($raw !== '') {
            $json = json_decode($raw, true);
            if (is_array($json) && isset($json['csrf_token'])) {
                $submitted = (string) $json['csrf_token'];
            }
        }
    }
    return $submitted !== '' && hash_equals((string) $_SESSION['csrf_token'], $submitted);
}

function requirePost(): void
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        header('Allow: POST');
        exit('Method Not Allowed');
    }
}

function setFlash(string $type, string $message): void
{
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function takeFlash(): ?array
{
    $flash = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);
    return is_array($flash) ? $flash : null;
}

function booking(string $bookingId): ?array
{
    $record = $_SESSION['bookings'][$bookingId] ?? null;
    return is_array($record) ? $record : null;
}

function redirectTo(string $path): never
{
    header('Location: ' . $path);
    exit;
}

function checkoutSteps(int $active): string
{
    $labels = ['Traveler', 'Review', 'Payment', 'Confirmed'];
    $html = '<ol class="steps" aria-label="Checkout progress">';
    foreach ($labels as $index => $label) {
        $number = $index + 1;
        $state = $number < $active ? ' complete' : ($number === $active ? ' active' : '');
        $html .= '<li class="step' . $state . '"><span>' . $number . '</span><strong>' . escape($label) . '</strong></li>';
    }
    return $html . '</ol>';
}

function getFlag(): string
{
    // 1. Explicit platform environment variable injection (e.g. from orchestrator)
    $envFlag = getenv('CTF_FLAG') ?: ($_ENV['CTF_FLAG'] ?? ($_SERVER['CTF_FLAG'] ?? ''));
    if (is_string($envFlag) && trim($envFlag) !== '' && trim($envFlag) !== 'CTF{checkout_complete_payment_incomplete}') {
        return trim($envFlag);
    }

    // 2. Consistent session flag (persists across requests for the user's session)
    if (!empty($_SESSION['ctf_flag']) && is_string($_SESSION['ctf_flag'])) {
        return $_SESSION['ctf_flag'];
    }

    // 3. Container flag file (if written by entrypoint or platform volume)
    $flagFile = '/var/www/flag.txt';
    if (file_exists($flagFile) && is_readable($flagFile)) {
        $fileFlag = trim((string) @file_get_contents($flagFile));
        if ($fileFlag !== '' && $fileFlag !== 'CTF{checkout_complete_payment_incomplete}') {
            $_SESSION['ctf_flag'] = $fileFlag;
            return $fileFlag;
        }
    }

    // 4. Deterministic dynamic generation if a user seed / identifier is present
    $userSeed = getenv('USER_SEED') ?: (getenv('USER_ID') ?: (getenv('STUDENT_ID') ?: ($_ENV['USER_SEED'] ?? ($_ENV['USER_ID'] ?? ''))));
    if (is_string($userSeed) && trim($userSeed) !== '') {
        $hash = substr(hash('sha256', 'a06_medium_salt_4812:' . trim($userSeed)), 0, 16);
        $flag = "CTF{checkout_complete_payment_{$hash}}";
        $_SESSION['ctf_flag'] = $flag;
        return $flag;
    }

    // 5. Autonomous cryptographically random dynamic flag per user session / instance
    $token = bin2hex(random_bytes(8));
    $flag = "CTF{checkout_complete_payment_{$token}}";
    $_SESSION['ctf_flag'] = $flag;
    return $flag;
}


