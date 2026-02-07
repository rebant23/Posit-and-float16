
import math

def int_to_posit16(n: int, es: int) -> str:
    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if n == 0:
        return "0" * 16

    neg = n < 0
    n = abs(n)

    useed = 2 ** (2 ** es)

    # --- regime k ---
    k = int(math.floor(math.log(n, useed)))

    # --- regime bits ---
    if k >= 0:
        regime = "1" * (k + 1) + "0"
    else:
        regime = "0" * (-k) + "1"

    # --- scaled value ---
    scaled = n / (useed ** k)

    # --- exponent ---
    exp = 0
    if es > 0:
        exp = int(math.floor(math.log2(scaled)))
        exp = max(0, min(exp, (1 << es) - 1))
        scaled /= (2 ** exp)

    exp_bits = format(exp, f"0{es}b")

    used = 1 + len(regime) + es
    if used >= 16:
        final = 0x7FFF
    else:
        frac = scaled - 1
        frac_bits = ""
        for _ in range(16 - used + 1):  # guard bit
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        raw = "0" + regime + exp_bits + frac_bits
        final = int(raw[:16], 2)

        # round-to-nearest
        if len(raw) > 16 and raw[16] == "1":
            final += 1

        final = min(final, 0x7FFF)

    if neg:
        final = (~final + 1) & 0xFFFF

    return format(final, "016b")

print(int_to_posit16(5.5, 1))

import math

def int_to_posit16_0(n: int) -> str:
    """
    Convert integer to posit(16,0) binary string.
    Simple truncation rounding (matches tochinet-style behavior).
    """

    if n == 0:
        return "0" * 16

    neg = n < 0
    n = abs(n)

    # --- regime k (power of 2) ---
    k = int(math.floor(math.log2(n)))

    # --- regime bits ---
    # k >= 0 always for integer >= 1
    regime = "1" * (k + 1) + "0"

    # --- check overflow ---
    if 1 + len(regime) >= 16:
        posit = "0" + "1" * 14 + "1"  # 0111111111111111
    else:
        # --- scaled value ---
        scaled = n / (2 ** k)  # in [1, 2)

        # --- fraction ---
        frac = scaled - 1
        frac_bits = ""
        remaining = 16 - (1 + len(regime))

        for _ in range(remaining):
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        posit = "0" + regime + frac_bits
        posit = posit[:16].ljust(16, "0")

    # --- two’s complement for negatives ---
    if neg:
        val = int(posit, 2)
        val = (~val + 1) & 0xFFFF
        posit = format(val, "016b")

    return posit
print(int_to_posit16_0(-5))

def posit16_to_float(p: str, es: int) -> float:
    """
    Convert posit(16, es) binary string to decimal float.
    Supports es = 0, 1, 2.
    """

    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if len(p) != 16 or any(c not in "01" for c in p):
        raise ValueError("Input must be a 16-bit binary string")

    # Zero
    if p == "0" * 16:
        return 0.0

    # --- sign / two's complement ---
    neg = p[0] == "1"
    if neg:
        val = int(p, 2)
        val = (~val + 1) & 0xFFFF
        p = format(val, "016b")

    useed = 2 ** (2 ** es)

    # --- regime ---
    i = 1
    regime_bit = p[i]
    run = 0

    while i < 16 and p[i] == regime_bit:
        run += 1
        i += 1

    if regime_bit == "1":
        k = run - 1
    else:
        k = -run

    # skip terminating bit
    i += 1

    # --- exponent ---
    exp = 0
    if es > 0 and i + es <= 16:
        exp = int(p[i:i+es], 2)
        i += es

    # --- fraction ---
    frac = 0.0
    scale = 0.5
    while i < 16:
        if p[i] == "1":
            frac += scale
        scale /= 2
        i += 1

    value = (useed ** k) * (2 ** exp) * (1 + frac)

    return -value if neg else value

print(posit16_to_float("1000110011100110", 0))

def decode_posit16(p: int, es: int):
    if p == 0:
        return 0, 0, 0

    neg = (p & 0x8000) != 0
    if neg:
        p = (~p + 1) & 0xFFFF

    i = 14
    rb = (p >> i) & 1
    run = 0

    while i >= 0 and ((p >> i) & 1) == rb:
        run += 1
        i -= 1

    k = run - 1 if rb else -run

    exp = 0
    if es > 0:
        exp = (p >> (i - es + 1)) & ((1 << es) - 1)
        i -= es

    scale = k * (1 << es) + exp

    frac_len = i + 1
    frac = p & ((1 << frac_len) - 1)

    # 🔥 Q1.16 fixed-point mantissa
    mantissa = (1 << 16) | (frac << (16 - frac_len))

    return (-1 if neg else 1), scale, mantissa

def encode_posit16(sign, scale, mantissa, es):
    if mantissa == 0:
        return 0

    # normalize mantissa
    while mantissa >= (1 << 15):
        mantissa >>= 1
        scale += 1

    while mantissa < (1 << 14):
        mantissa <<= 1
        scale -= 1

    k = scale >> es
    exp = scale & ((1 << es) - 1)

    # regime
    if k >= 0:
        regime_bits = ('1' * (k + 1)) + '0'
    else:
        regime_bits = ('0' * (-k)) + '1'

    exp_bits = format(exp, f'0{es}b') if es > 0 else ''
    frac_bits = format(mantissa & ((1 << 14) - 1), '014b')

    posit_bits = regime_bits + exp_bits + frac_bits
    posit_bits = posit_bits[:15].ljust(15, '0')

    posit = int(posit_bits, 2)

    if sign < 0:
        posit = (~posit + 1) & 0xFFFF

    return posit

def align(m, shift):
    if shift <= 0:
        return m
    if shift >= 16:
        return 1  # sticky only
    sticky = 1 if (m & ((1 << shift) - 1)) else 0
    return (m >> shift) | sticky

def posit16_add(pa: int, pb: int, es: int) -> int:
    sa, ka, ma = decode_posit16(pa, es)
    sb, kb, mb = decode_posit16(pb, es)

    # align scales
    if ka > kb:
        mb = align(mb, ka - kb)
        k = ka
    else:
        ma = align(ma, kb - ka)
        k = kb

    # add mantissas
    m = sa * ma + sb * mb
    if m == 0:
        return 0

    sign = -1 if m < 0 else 1
    m = abs(m)

    # 🔥 normalization for Q1.16
    if m >= (1 << 17):   # overflow (>= 2.0)
        m >>= 1
        k += 1

    return encode_posit16(sign, k, m >> 2, es)
    # >>2 drops guard bits back to Q1.14 for encoder

def posit_add_integers(a: int, b: int, es: int):
    # --- int → posit (BITSTRING) ---
    if es == 0:
        pa_str = int_to_posit16_0(a)
        pb_str = int_to_posit16_0(b)
    else:
        pa_str = int_to_posit16(a, es)
        pb_str = int_to_posit16(b, es)

    # --- convert bitstring → integer for hardware ---
    pa = int(pa_str, 2)
    pb = int(pb_str, 2)

    # --- posit-domain hardware add ---
    ps = posit16_add(pa, pb, es)

    # --- convert result back to bitstring ---
    ps_str = format(ps, "016b")

    # --- decode for display ---
    value = posit16_to_float(ps_str, es)

    return {
        "a_posit": pa_str,
        "b_posit": pb_str,
        "sum_posit": ps_str,
        "sum_decimal": value,
        "sum_integer": int(value)
    }

es = 2
a = 5
b = 3

r = posit_add_integers(a, b, es)

for k, v in r.items():
    print(k, ":", v)