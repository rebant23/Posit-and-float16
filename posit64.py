import math

def int_to_posit64(n: int, es: int) -> str:
    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if n == 0:
        return "0" * 64

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
    if used >= 64:
        final = 0x7FFFFFFFFFFFFFFF
    else:
        frac = scaled - 1
        frac_bits = ""
        for _ in range(64 - used + 1):  # guard bit
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        raw = "0" + regime + exp_bits + frac_bits
        final = int(raw[:64], 2)

        # round-to-nearest
        if len(raw) > 64 and raw[64] == "1":
            final += 1

        final = min(final, 0x7FFFFFFFFFFFFFFF)

    if neg:
        final = (~final + 1) & 0xFFFFFFFFFFFFFFFF

    return format(final, "064b")

import math

def int_to_posit64_0(n: int) -> str:
    """
    Convert integer to posit(64,0) binary string.
    Simple truncation rounding (matches tochinet-style behavior).
    """

    if n == 0:
        return "0" * 64

    neg = n < 0
    n = abs(n)

    # --- regime k (power of 2) ---
    k = int(math.floor(math.log2(n)))

    # --- regime bits ---
    regime = "1" * (k + 1) + "0"

    # --- check overflow ---
    if 1 + len(regime) >= 64:
        posit = "0" + "1" * 62 + "1"  # 0 + 63 ones
    else:
        # --- scaled value ---
        scaled = n / (2 ** k)

        # --- fraction ---
        frac = scaled - 1
        frac_bits = ""
        remaining = 64 - (1 + len(regime))

        for _ in range(remaining):
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        posit = "0" + regime + frac_bits
        posit = posit[:64].ljust(64, "0")

    # --- two’s complement for negatives ---
    if neg:
        val = int(posit, 2)
        val = (~val + 1) & 0xFFFFFFFFFFFFFFFF
        posit = format(val, "064b")

    return posit

def posit64_to_float(p: str, es: int) -> float:
    """
    Convert posit(64, es) binary string to decimal float.
    Supports es = 0, 1, 2.
    """

    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if len(p) != 64 or any(c not in "01" for c in p):
        raise ValueError("Input must be a 64-bit binary string")

    # Zero
    if p == "0" * 64:
        return 0.0

    # --- sign / two's complement ---
    neg = p[0] == "1"
    if neg:
        val = int(p, 2)
        val = (~val + 1) & 0xFFFFFFFFFFFFFFFF
        p = format(val, "064b")

    useed = 2 ** (2 ** es)

    # --- regime ---
    i = 1
    regime_bit = p[i]
    run = 0

    while i < 64 and p[i] == regime_bit:
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
    if es > 0 and i + es <= 64:
        exp = int(p[i:i+es], 2)
        i += es

    # --- fraction ---
    frac = 0.0
    scale = 0.5
    while i < 64:
        if p[i] == "1":
            frac += scale
        scale /= 2
        i += 1

    value = (useed ** k) * (2 ** exp) * (1 + frac)

    return -value if neg else value

def decode_posit64(p: int, es: int):
    # 1. Handle Special Cases
    if p == 0:
        return 0, 0, 0
    if p == 0x8000000000000000:
        return None, None, None  # NaR

    # 2. Decode Sign & 2's Complement
    neg = (p & 0x8000000000000000) != 0
    if neg:
        p = (~p + 1) & 0xFFFFFFFFFFFFFFFF

    # 3. Decode Regime
    i = 62
    rb = (p >> i) & 1
    run = 0

    while i >= 0 and ((p >> i) & 1) == rb:
        run += 1
        i -= 1

    k = run - 1 if rb else -run

    # 4. Skip Terminator
    if i >= 0:
        i -= 1

    # 5. Decode Exponent
    exp = 0
    if es > 0:
        if i >= 0:
            shift = max(0, i - es + 1)
            bits_to_read = min(es, i + 1)

            exp = (p >> shift) & ((1 << bits_to_read) - 1)

            if bits_to_read < es:
                exp <<= (es - bits_to_read)

            i -= es
        else:
            exp = 0

    scale = k * (1 << es) + exp

    # 6. Decode Mantissa
    frac_len = max(0, i + 1)
    frac = 0
    if frac_len > 0:
        frac = p & ((1 << frac_len) - 1)

    # Normalize to Q1.64
    mantissa = (1 << 64) | (frac << (64 - frac_len))

    return (-1 if neg else 1), scale, mantissa

def encode_posit64(sign, scale, mantissa, es):
    if mantissa == 0:
        return 0

    # normalize mantissa
    while mantissa >= (1 << 63):
        mantissa >>= 1
        scale += 1

    while mantissa < (1 << 62):
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
    frac_bits = format(mantissa & ((1 << 62) - 1), '062b')

    posit_bits = regime_bits + exp_bits + frac_bits
    posit_bits = posit_bits[:63].ljust(63, '0')

    posit = int(posit_bits, 2)

    if sign < 0:
        posit = (~posit + 1) & 0xFFFFFFFFFFFFFFFF

    return posit

def align(m, shift):
    if shift <= 0:
        return m
    if shift >= 64:
        return 1  # sticky only
    sticky = 1 if (m & ((1 << shift) - 1)) else 0
    return (m >> shift) | sticky

def posit64_add(pa: int, pb: int, es: int) -> int:
    sa, ka, ma = decode_posit64(pa, es)
    sb, kb, mb = decode_posit64(pb, es)

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

    # 🔥 normalization for Q1.64
    if m >= (1 << 65):   # overflow (>= 2.0)
        m >>= 1
        k += 1

    return encode_posit64(sign, k, m >> 2, es)
    # >>2 drops guard bits back to Q1.62 for encoder

def posit_add_64(a: int, b: int, es: int):
    # --- int → posit (BITSTRING) ---
    if es == 0:
        pa_str = int_to_posit64_0(a)
        pb_str = int_to_posit64_0(b)
    else:
        pa_str = int_to_posit64(a, es)
        pb_str = int_to_posit64(b, es)

    # --- convert bitstring → integer for hardware ---
    pa = int(pa_str, 2)
    pb = int(pb_str, 2)

    # --- posit-domain hardware add ---
    ps = posit64_add(pa, pb, es)

    # --- convert result back to bitstring ---
    ps_str = format(ps, "064b")

    # --- decode for display ---
    value = posit64_to_float(ps_str, es)

    return {
        "a_posit": pa_str,
        "b_posit": pb_str,
        "sum_posit": ps_str,
        "sum_decimal": value,
        "sum_integer": int(value)
    }

def posit64_mul(pa: int, pb: int, es: int) -> int:
    sa, ka, ma = decode_posit64(pa, es)
    sb, kb, mb = decode_posit64(pb, es)

    # --- special cases ---
    if sa is None or sb is None:
        return 0x8000000000000000
    if ma == 0 or mb == 0:
        return 0

    sign = sa * sb
    k = ka + kb

    # Q1.64 × Q1.64 → Q2.128
    prod = ma * mb

    # ---- shift back to Q1.64 ----
    m = prod >> 64
    rem = prod & ((1 << 64) - 1)

    # ---- guard + sticky ----
    guard = (rem >> 63) & 1
    sticky = 1 if (rem & ((1 << 63) - 1)) else 0

    # ---- normalization ----
    if m >= (1 << 65):   # ≥ 2.0
        m >>= 1
        k += 1

    while m < (1 << 64): # < 1.0
        m <<= 1
        k -= 1

    # ---- round to nearest even ----
    lsb = m & 1
    if guard and (sticky or lsb):
        m += 1
        if m >= (1 << 65):
            m >>= 1
            k += 1

    # encoder expects Q1.62
    return encode_posit64(sign, k, m >> 2, es)

def posit64_mul_es0(pa: int, pb: int) -> int:
    sa, ka, ma = decode_posit64(pa, es=0)
    sb, kb, mb = decode_posit64(pb, es=0)

    # --- special cases ---
    if sa is None or sb is None:
        return 0x8000000000000000
    if ma == 0 or mb == 0:
        return 0

    sign = sa * sb
    k = ka + kb

    # Q1.64 × Q1.64 → Q2.128
    prod = ma * mb

    # shift back to Q1.64
    m = prod >> 64
    rem = prod & 0xFFFFFFFFFFFFFFFF

    # guard + sticky
    guard = (rem >> 63) & 1
    sticky = 1 if (rem & 0x7FFFFFFFFFFFFFFF) else 0

    # ---- single-step normalization ONLY ----
    if m >= (1 << 65):
        m >>= 1
        k += 1

    # ---- round-to-nearest-even ----
    lsb = m & 1
    if guard and (sticky or lsb):
        m += 1
        if m >= (1 << 65):
            m >>= 1
            k += 1

    # encoder expects Q1.62
    return encode_posit64(sign, k, m >> 2, es=0)

def posit_mul_64(a: float, b: float, es: int):
    # --- int → posit (BITSTRING) ---
    if es == 0:
        pa_str = int_to_posit64_0(a)
        pb_str = int_to_posit64_0(b)
    else:
        pa_str = int_to_posit64(a, es)
        pb_str = int_to_posit64(b, es)

    # --- bitstring → integer ---
    pa = int(pa_str, 2)
    pb = int(pb_str, 2)

    if es == 0:
        pp = posit64_mul_es0(pa, pb)
    else:
        pp = posit64_mul(pa, pb, es)

    # --- back to bitstring ---
    pp_str = format(pp, "064b")

    # --- decode for display ---
    value = posit64_to_float(pp_str, es)

    return {
        "a_posit": pa_str,
        "b_posit": pb_str,
        "prod_posit": pp_str,
        "prod_decimal": value
    }

def mul(num1: float, num2: float, es: int = 1) -> float:
    # --- decimal → posit bitstring ---
    if es == 0:
        p1_str = int_to_posit64_0(num1)
        p2_str = int_to_posit64_0(num2)
    else:
        p1_str = int_to_posit64(num1, es)
        p2_str = int_to_posit64(num2, es)

    # --- bitstring → integer (hardware form) ---
    p1 = int(p1_str, 2)
    p2 = int(p2_str, 2)

    # --- posit-domain multiply ---
    p_prod = posit64_mul(p1, p2, es)

    # --- back to decimal ---
    return posit64_to_float(format(p_prod, "064b"), es)

def add(num1: float, num2: float, es: int = 1) -> float:
    # --- decimal → posit bitstring ---
    if es == 0:
        p1_str = int_to_posit64_0(num1)
        p2_str = int_to_posit64_0(num2)
    else:
        p1_str = int_to_posit64(num1, es)
        p2_str = int_to_posit64(num2, es)

    # --- bitstring → integer (hardware form) ---
    p1 = int(p1_str, 2)
    p2 = int(p2_str, 2)

    # --- posit-domain add ---
    p_sum = posit64_add(p1, p2, es)

    # --- back to decimal ---
    return posit64_to_float(format(p_sum, "064b"), es)
