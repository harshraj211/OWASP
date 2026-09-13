<?php

declare(strict_types=1);

session_name('northstar_store');
session_set_cookie_params([
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_start();

const STARTING_BALANCE_CENTS = 7500;

if (!isset($_SESSION['balance_cents'], $_SESSION['orders'])) {
    $_SESSION['balance_cents'] = STARTING_BALANCE_CENTS;
    $_SESSION['orders'] = [];
}

function catalog(): array
{
    return [
        'field-notes' => [
            'name' => 'Pocket Notebook Set',
            'description' => 'Three durable notebooks for plans, sketches, and everyday ideas.',
            'price_cents' => 2400,
            'eyebrow' => 'Stationery',
            'visual' => 'notes',
        ],
        'security-key' => [
            'name' => 'Titanium USB Drive',
            'description' => 'A compact metal archive drive for work, study, and travel.',
            'price_cents' => 6800,
            'eyebrow' => 'Storage',
            'visual' => 'key',
        ],
        'vault-case' => [
            'name' => 'Redline Travel Case',
            'description' => 'A limited-edition hard case from the Northstar premium collection.',
            'price_cents' => 125000,
            'eyebrow' => 'Limited edition',
            'visual' => 'case',
            'premium' => true,
        ],
    ];
}

function escape(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function money(int $cents): string
{
    $sign = $cents < 0 ? '-' : '';
    return $sign . '$' . number_format(abs($cents) / 100, 2);
}

function submittedPriceToCents(string $value): ?int
{
    if (!preg_match('/^-?\d{1,7}(?:\.\d{1,2})?$/', $value)) {
        return null;
    }

    $negative = str_starts_with($value, '-');
    $unsigned = ltrim($value, '-');
    [$whole, $fraction] = array_pad(explode('.', $unsigned, 2), 2, '');
    $fraction = str_pad($fraction, 2, '0');
    $cents = ((int) $whole * 100) + (int) $fraction;

    return $negative ? -$cents : $cents;
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

function redirectHome(): never
{
    header('Location: ./');
    exit;
}

function getFlag(): string
{
    // 1. Explicit platform environment variable injection (e.g. from orchestrator)
    $envFlag = getenv('CTF_FLAG') ?: ($_ENV['CTF_FLAG'] ?? ($_SERVER['CTF_FLAG'] ?? ''));
    if (is_string($envFlag) && trim($envFlag) !== '' && trim($envFlag) !== 'CTF{negative_price_positive_profit}') {
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
        if ($fileFlag !== '' && $fileFlag !== 'CTF{negative_price_positive_profit}') {
            $_SESSION['ctf_flag'] = $fileFlag;
            return $fileFlag;
        }
    }

    // 4. Deterministic dynamic generation if a user seed / identifier is present
    $userSeed = getenv('USER_SEED') ?: (getenv('USER_ID') ?: (getenv('STUDENT_ID') ?: ($_ENV['USER_SEED'] ?? ($_ENV['USER_ID'] ?? ''))));
    if (is_string($userSeed) && trim($userSeed) !== '') {
        $hash = substr(hash('sha256', 'a06_easy_salt_9281:' . trim($userSeed)), 0, 16);
        $flag = "CTF{negative_price_positive_profit_{$hash}}";
        $_SESSION['ctf_flag'] = $flag;
        return $flag;
    }

    // 5. Autonomous cryptographically random dynamic flag per user session / instance
    $token = bin2hex(random_bytes(8));
    $flag = "CTF{negative_price_positive_profit_{$token}}";
    $_SESSION['ctf_flag'] = $flag;
    return $flag;
}

