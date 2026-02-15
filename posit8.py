import math

def int_to_posit8(n: int, es: int) -> str:
    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if n == 0:
        return "0" * 8

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
    if used >= 8:
        final = 0x7F
    else:
        frac = scaled - 1
        frac_bits = ""
        for _ in range(8 - used + 1):  # guard bit
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        raw = "0" + regime + exp_bits + frac_bits
        final = int(raw[:8], 2)

        # round-to-nearest
        if len(raw) > 8 and raw[8] == "1":
            final += 1

        final = min(final, 0x7F)

    if neg:
        final = (~final + 1) & 0xFF

    return format(final, "08b")

#print(int_to_posit8(-5.7575,2))
import math

def int_to_posit8_0(n: int) -> str:
    """
    Convert integer to posit(8,0) binary string.
    Simple truncation rounding (matches tochinet-style behavior).
    """

    if n == 0:
        return "0" * 8

    neg = n < 0
    n = abs(n)

    # --- regime k (power of 2) ---
    k = int(math.floor(math.log2(n)))

    # --- regime bits ---
    # k >= 0 always for integer >= 1
    regime = "1" * (k + 1) + "0"

    # --- check overflow ---
    if 1 + len(regime) >= 8:
        posit = "0" + "1" * 6 + "1"  # 01111111
    else:
        # --- scaled value ---
        scaled = n / (2 ** k)  # in [1, 2)

        # --- fraction ---
        frac = scaled - 1
        frac_bits = ""
        remaining = 8 - (1 + len(regime))

        for _ in range(remaining):
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        posit = "0" + regime + frac_bits
        posit = posit[:8].ljust(8, "0")

    # --- two’s complement for negatives ---
    if neg:
        val = int(posit, 2)
        val = (~val + 1) & 0xFF
        posit = format(val, "08b")

    return posit
#print(int_to_posit8_0(-5.7575))

def posit8_to_float(p: str, es: int) -> float:
    """
    Convert posit(8, es) binary string to decimal float.
    Supports es = 0, 1, 2.
    """

    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if len(p) != 8 or any(c not in "01" for c in p):
        raise ValueError("Input must be an 8-bit binary string")

    # Zero
    if p == "0" * 8:
        return 0.0

    # --- sign / two's complement ---
    neg = p[0] == "1"
    if neg:
        val = int(p, 2)
        val = (~val + 1) & 0xFF
        p = format(val, "08b")

    useed = 2 ** (2 ** es)

    # --- regime ---
    i = 1
    regime_bit = p[i]
    run = 0

    while i < 8 and p[i] == regime_bit:
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
    if es > 0 and i + es <= 8:
        exp = int(p[i:i+es], 2)
        i += es

    # --- fraction ---
    frac = 0.0
    scale = 0.5
    while i < 8:
        if p[i] == "1":
            frac += scale
        scale /= 2
        i += 1

    value = (useed ** k) * (2 ** exp) * (1 + frac)

    return -value if neg else value

def decode_posit8(p: int, es: int):
    # 1. Handle Special Cases
    if p == 0:
        return 0, 0, 0        # Zero
    if p == 0x80:
        return None, None, None # NaR (Not a Real) / Infinity

    # 2. Decode Sign & 2's Complement
    neg = (p & 0x80) != 0
    if neg:
        p = (~p + 1) & 0xFF
        # Note: In Python, 0x80 would cause issues here if not handled above,
        # but we already returned None for it.

    # 3. Decode Regime
    i = 6
    rb = (p >> i) & 1
    run = 0

    # Iterate while bits match the regime bit (rb)
    while i >= 0 and ((p >> i) & 1) == rb:
        run += 1
        i -= 1

    k = run - 1 if rb else -run

    # 4. Skip Terminator (CRITICAL FIX)
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

    # Normalize to Q1.8 (1.xxxxxxxx)
    mantissa = (1 << 8) | (frac << (8 - frac_len))

    return (-1 if neg else 1), scale, mantissa

def encode_posit8(sign, scale, mantissa, es):
    if mantissa == 0:
        return 0

    # normalize mantissa
    while mantissa >= (1 << 7):
        mantissa >>= 1
        scale += 1

    while mantissa < (1 << 6):
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
    frac_bits = format(mantissa & ((1 << 6) - 1), '06b')

    posit_bits = regime_bits + exp_bits + frac_bits
    posit_bits = posit_bits[:7].ljust(7, '0')

    posit = int(posit_bits, 2)

    if sign < 0:
        posit = (~posit + 1) & 0xFF

    return posit


def align(m, shift):
    if shift <= 0:
        return m
    if shift >= 8:
        return 1  # sticky only
    sticky = 1 if (m & ((1 << shift) - 1)) else 0
    return (m >> shift) | sticky

def posit8_add(pa: int, pb: int, es: int) -> int:
    sa, ka, ma = decode_posit8(pa, es)
    sb, kb, mb = decode_posit8(pb, es)

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

    # 🔥 normalization for Q1.8
    if m >= (1 << 9):   # overflow (>= 2.0)
        m >>= 1
        k += 1

    return encode_posit8(sign, k, m >> 2, es)
    # >>2 drops guard bits back to Q1.6 for encoder


def posit_add(a: int, b: int, es: int):
    # --- int → posit (BITSTRING) ---
    if es == 0:
        pa_str = int_to_posit8_0(a)
        pb_str = int_to_posit8_0(b)
    else:
        pa_str = int_to_posit8(a, es)
        pb_str = int_to_posit8(b, es)

    # --- convert bitstring → integer for hardware ---
    pa = int(pa_str, 2)
    pb = int(pb_str, 2)

    # --- posit-domain hardware add ---
    ps = posit8_add(pa, pb, es)

    # --- convert result back to bitstring ---
    ps_str = format(ps, "08b")

    # --- decode for display ---
    value = posit8_to_float(ps_str, es)

    return {
        "a_posit": pa_str,
        "b_posit": pb_str,
        "sum_posit": ps_str,
        "sum_decimal": value,
        "sum_integer": int(value)
    }

def posit8_mul(pa: int, pb: int, es: int) -> int:
    sa, ka, ma = decode_posit8(pa, es)
    sb, kb, mb = decode_posit8(pb, es)

    # --- special cases ---
    if sa is None or sb is None:
        return 0x80
    if ma == 0 or mb == 0:
        return 0

    sign = sa * sb
    k = ka + kb

    # Q1.8 × Q1.8 → Q2.16
    prod = ma * mb

    # ---- shift back to Q1.8 (CRITICAL FIX) ----
    m = prod >> 8
    rem = prod & ((1 << 8) - 1)

    # ---- guard + sticky ----
    guard = (rem >> 7) & 1
    sticky = 1 if (rem & ((1 << 7) - 1)) else 0

    # ---- normalization ----
    if m >= (1 << 9):   # ≥ 2.0
        m >>= 1
        k += 1

    while m < (1 << 8): # < 1.0
        m <<= 1
        k -= 1

    # ---- round to nearest even ----
    lsb = m & 1
    if guard and (sticky or lsb):
        m += 1
        if m >= (1 << 9):
            m >>= 1
            k += 1

    # encoder expects Q1.6
    return encode_posit8(sign, k, m >> 2, es)


def posit8_mul_es0(pa: int, pb: int) -> int:
    sa, ka, ma = decode_posit8(pa, es=0)
    sb, kb, mb = decode_posit8(pb, es=0)

    # --- special cases ---
    if sa is None or sb is None:
        return 0x80
    if ma == 0 or mb == 0:
        return 0

    sign = sa * sb
    k = ka + kb

    # Q1.8 × Q1.8 → Q2.16
    prod = ma * mb

    # shift back to Q1.8
    m = prod >> 8
    rem = prod & 0xFF

    # guard + sticky
    guard = (rem >> 7) & 1
    sticky = 1 if (rem & 0x7F) else 0

    # ---- single-step normalization ONLY ----
    if m >= (1 << 9):        # ≥ 2.0
        m >>= 1
        k += 1

    # ---- round-to-nearest-even ----
    lsb = m & 1
    if guard and (sticky or lsb):
        m += 1
        if m >= (1 << 9):
            m >>= 1
            k += 1

    # encoder expects Q1.6
    return encode_posit8(sign, k, m >> 2, es=0)


def posit_mul(a: float, b: float, es: int):
    # --- int → posit (BITSTRING) ---
    if es == 0:
        pa_str = int_to_posit8_0(a)
        pb_str = int_to_posit8_0(b)
    else:
        pa_str = int_to_posit8(a, es)
        pb_str = int_to_posit8(b, es)

    # --- bitstring → integer ---
    pa = int(pa_str, 2)
    pb = int(pb_str, 2)

    if es == 0:
        pp = posit8_mul_es0(pa, pb)
    else:
        pp = posit8_mul(pa, pb, es)
    
    # --- back to bitstring ---
    pp_str = format(pp, "08b")

    # --- decode for display ---
    value = posit8_to_float(pp_str, es)

    return {
        "a_posit": pa_str,
        "b_posit": pb_str,
        "prod_posit": pp_str,
        "prod_decimal": value
    }

def mul(num1: float, num2: float, es: int = 1) -> float:
    # --- decimal → posit bitstring ---
    if es == 0:
        p1_str = int_to_posit8_0(num1)
        p2_str = int_to_posit8_0(num2)
    else:
        p1_str = int_to_posit8(num1, es)
        p2_str = int_to_posit8(num2, es)

    # --- bitstring → integer (hardware form) ---
    p1 = int(p1_str, 2)
    p2 = int(p2_str, 2)

    # --- posit-domain multiply ---
    p_prod = posit8_mul(p1, p2, es)

    # --- back to decimal ---
    return posit8_to_float(format(p_prod, "08b"), es)

def add(num1: float, num2: float, es: int = 1) -> float:
    # --- decimal → posit bitstring ---
    if es == 0:
        p1_str = int_to_posit8_0(num1)
        p2_str = int_to_posit8_0(num2)
    else:
        p1_str = int_to_posit8(num1, es)
        p2_str = int_to_posit8(num2, es)

    # --- bitstring → integer (hardware form) ---
    p1 = int(p1_str, 2)
    p2 = int(p2_str, 2)

    # --- posit-domain add ---
    p_sum = posit8_add(p1, p2, es)

    # --- back to decimal ---
    return posit8_to_float(format(p_sum, "08b"), es)

