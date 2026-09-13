<?php

declare(strict_types=1);

const STARTING_BALANCE_CENTS = 5000; // ₹50.00
const DEV_SIGNING_SECRET = 'apex_dev_sec_994821';

require_once __DIR__ . '/db.php';

session_name('apex_vault_session');
session_set_cookie_params([
    'httponly' => true,
    'samesite' => 'Lax',
]);
session_start();

if (!isset($_SESSION['user_id'])) {
    $_SESSION['user_id'] = 'usr_' . substr(bin2hex(random_bytes(6)), 0, 10);
    $_SESSION['csrf_token'] = bin2hex(random_bytes(24));
}

$user = getUserData($_SESSION['user_id']);

// Issue / initialize tier cookie if not present
if (!isset($_COOKIE['apex_member_tier'])) {
    $tierPayload = json_encode([
        'user_id' => $_SESSION['user_id'],
        'tier' => $user['tier'] ?? 'standard',
        'issued_at' => time(),
    ]);
    $tierB64 = base64_encode($tierPayload);
    $sig = hash_hmac('sha256', $tierB64, DEV_SIGNING_SECRET);
    setcookie('apex_member_tier', $tierB64 . '.' . $sig, [
        'httponly' => false,
        'samesite' => 'Lax',
        'path' => '/',
    ]);
}

// Release session lock so parallel requests can run concurrently
session_write_close();

function getUserTier(): string
{
    if (isset($_COOKIE['apex_member_tier'])) {
        $parts = explode('.', $_COOKIE['apex_member_tier'], 2);
        if (count($parts) === 2) {
            [$payloadB64, $sig] = $parts;
            // Verify HMAC signature with developer secret
            $expectedSig = hash_hmac('sha256', $payloadB64, DEV_SIGNING_SECRET);
            if (hash_equals($expectedSig, $sig)) {
                $data = json_decode(base64_decode($payloadB64), true);
                if (is_array($data) && isset($data['tier'])) {
                    return (string) $data['tier'];
                }
            }
        }
    }
    return 'standard';
}

function coupons(): array
{
    return [
        'WELCOME50' => [
            'code' => 'WELCOME50',
            'amount_cents' => 5000, // ₹50.00
            'description' => 'Welcome promotional voucher: ₹50.00 store credit',
        ],
        'APEXVIP' => [
            'code' => 'APEXVIP',
            'amount_cents' => 10000, // ₹100.00
            'description' => 'VIP member exclusive bonus: ₹100.00 store credit',
        ],
    ];
}

function catalog(): array
{
    return [
        'silver-emblem' => [
            'id' => 'silver-emblem',
            'name' => 'Sterling Silver Emblem',
            'description' => 'A minted collector emblem forged from pure sterling silver.',
            'price_cents' => 2500, // ₹25.00
            'tier_required' => 'standard',
            'icon' => 'emblem',
            'premium' => false,
        ],
        'platinum-pass' => [
            'id' => 'platinum-pass',
            'name' => 'Executive Club Pass',
            'description' => 'Full access credentials for high-tier member amenities.',
            'price_cents' => 15000, // ₹150.00
            'tier_required' => 'standard',
            'icon' => 'pass',
            'premium' => false,
        ],
        'obsidian-key' => [
            'id' => 'obsidian-key',
            'name' => 'Obsidian Sovereign Key',
            'description' => 'The ultimate cryptographic access key to the Sovereign Vault reserve.',
            'price_cents' => 5000000, // ₹50,000.00
            'tier_required' => 'sovereign_vip',
            'icon' => 'key',
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
    return $sign . '₹' . number_format(abs($cents) / 100, 2);
}

function csrfField(): string
{
    return '<input type="hidden" name="csrf_token" value="' . escape((string) ($_SESSION['csrf_token'] ?? '')) . '">';
}

function validCsrf(): bool
{
    $submitted = (string) ($_POST['csrf_token'] ?? ($_SERVER['HTTP_X_CSRF_TOKEN'] ?? ''));
    if ($submitted === '') {
        $raw = (string) @file_get_contents('php://input');
        if ($raw !== '') {
            $json = json_decode($raw, true);
            if (is_array($json) && isset($json['csrf_token'])) {
                $submitted = (string) $json['csrf_token'];
            }
        }
    }
    return $submitted !== '' && hash_equals((string) ($_SESSION['csrf_token'] ?? ''), $submitted);
}

function setFlash(string $type, string $message): void
{
    if (session_status() !== PHP_SESSION_ACTIVE) {
        @session_start();
    }
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
    session_write_close();
}

function takeFlash(): ?array
{
    if (session_status() !== PHP_SESSION_ACTIVE) {
        @session_start();
    }
    $flash = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);
    session_write_close();
    return is_array($flash) ? $flash : null;
}

function redirectHome(): never
{
    header('Location: ../');
    exit;
}

function getFlag(): string
{
    // 1. Explicit platform environment variable injection
    $envFlag = getenv('CTF_FLAG') ?: ($_ENV['CTF_FLAG'] ?? ($_SERVER['CTF_FLAG'] ?? ''));
    if (is_string($envFlag) && trim($envFlag) !== '' && trim($envFlag) !== 'CTF{coupon_wallet_design_abuse}') {
        return trim($envFlag);
    }

    // 2. Consistent session flag
    if (!empty($_SESSION['ctf_flag']) && is_string($_SESSION['ctf_flag'])) {
        return $_SESSION['ctf_flag'];
    }

    // 3. Container flag file
    $flagFile = '/var/www/flag.txt';
    if (file_exists($flagFile) && is_readable($flagFile)) {
        $fileFlag = trim((string) @file_get_contents($flagFile));
        if ($fileFlag !== '' && $fileFlag !== 'CTF{coupon_wallet_design_abuse}') {
            $_SESSION['ctf_flag'] = $fileFlag;
            return $fileFlag;
        }
    }

    // 4. Deterministic dynamic generation if a user seed / identifier is present
    $userSeed = getenv('USER_SEED') ?: (getenv('USER_ID') ?: (getenv('STUDENT_ID') ?: ($_ENV['USER_SEED'] ?? ($_ENV['USER_ID'] ?? ''))));
    if (is_string($userSeed) && trim($userSeed) !== '') {
        $hash = substr(hash('sha256', 'a06_hard_salt_7731:' . trim($userSeed)), 0, 16);
        $flag = "CTF{coupon_wallet_design_abuse_{$hash}}";
        $_SESSION['ctf_flag'] = $flag;
        return $flag;
    }

    // 5. Autonomous cryptographically random dynamic flag per user session / instance
    $token = bin2hex(random_bytes(8));
    $flag = "CTF{coupon_wallet_design_abuse_{$token}}";
    $_SESSION['ctf_flag'] = $flag;
    return $flag;
}
