<?php

declare(strict_types=1);

const DATA_DIR = '/var/www/data';

function ensureDataDir(): void
{
    if (!is_dir(DATA_DIR)) {
        @mkdir(DATA_DIR, 0777, true);
    }
    $usersDir = DATA_DIR . '/users';
    if (!is_dir($usersDir)) {
        @mkdir($usersDir, 0777, true);
    }
    $ordersDir = DATA_DIR . '/orders';
    if (!is_dir($ordersDir)) {
        @mkdir($ordersDir, 0777, true);
    }
}

function getUserFilePath(string $userId): string
{
    ensureDataDir();
    $safeId = preg_replace('/[^a-zA-Z0-9_-]/', '', $userId);
    return DATA_DIR . '/users/' . $safeId . '.json';
}

function getUserData(string $userId): array
{
    $filePath = getUserFilePath($userId);
    if (file_exists($filePath)) {
        $raw = (string) @file_get_contents($filePath);
        $data = json_decode($raw, true);
        if (is_array($data)) {
            return $data;
        }
    }

    $defaultData = [
        'user_id' => $userId,
        'balance_cents' => STARTING_BALANCE_CENTS,
        'tier' => 'standard',
        'redemptions' => [],
        'created_at' => gmdate('c'),
    ];
    saveUserData($userId, $defaultData);
    return $defaultData;
}

function saveUserData(string $userId, array $data): bool
{
    $filePath = getUserFilePath($userId);
    return (bool) @file_put_contents($filePath, json_encode($data, JSON_PRETTY_PRINT));
}

function getOrders(string $userId): array
{
    ensureDataDir();
    $ordersFile = DATA_DIR . '/orders/' . preg_replace('/[^a-zA-Z0-9_-]/', '', $userId) . '.json';
    if (file_exists($ordersFile)) {
        $raw = (string) @file_get_contents($ordersFile);
        $data = json_decode($raw, true);
        if (is_array($data)) {
            return $data;
        }
    }
    return [];
}

function saveOrder(string $userId, array $order): void
{
    ensureDataDir();
    $orders = getOrders($userId);
    array_unshift($orders, $order);
    $orders = array_slice($orders, 0, 10);
    $ordersFile = DATA_DIR . '/orders/' . preg_replace('/[^a-zA-Z0-9_-]/', '', $userId) . '.json';
    @file_put_contents($ordersFile, json_encode($orders, JSON_PRETTY_PRINT));
}

function resetUserData(string $userId): void
{
    ensureDataDir();
    $safeId = preg_replace('/[^a-zA-Z0-9_-]/', '', $userId);
    @unlink(DATA_DIR . '/users/' . $safeId . '.json');
    @unlink(DATA_DIR . '/orders/' . $safeId . '.json');
}
