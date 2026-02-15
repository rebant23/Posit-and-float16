import math

def int_to_posit32(n: float, es: int) -> str:
    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if n == 0:
        return "0" * 32

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

    if used >= 32:
        final = 0x7FFFFFFF
    else:
        frac = scaled - 1
        frac_bits = ""
        for _ in range(32 - used + 1):  # guard bit
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        raw = "0" + regime + exp_bits + frac_bits
        final = int(raw[:32], 2)

        # round-to-nearest
        if len(raw) > 32 and raw[32] == "1":
            final += 1

        final = min(final, 0x7FFFFFFF)

    if neg:
        final = (~final + 1) & 0xFFFFFFFF

    return format(final, "032b")

#print(int_to_posit32(-5.757575,1))

def int_to_posit32_0(n: int) -> str:
    """
    Convert integer to posit(32,0) binary string.
    Simple truncation rounding (matches tochinet-style behavior).
    """

    if n == 0:
        return "0" * 32

    neg = n < 0
    n = abs(n)

    # --- regime k (power of 2) ---
    k = int(math.floor(math.log2(n)))

    # --- regime bits ---
    regime = "1" * (k + 1) + "0"

    # --- check overflow ---
    if 1 + len(regime) >= 32:
        posit = "0" + "1" * 30 + "1"  # 011111...111 (31 ones total)
    else:
        # --- scaled value ---
        scaled = n / (2 ** k)

        # --- fraction ---
        frac = scaled - 1
        frac_bits = ""
        remaining = 32 - (1 + len(regime))

        for _ in range(remaining):
            frac *= 2
            if frac >= 1:
                frac_bits += "1"
                frac -= 1
            else:
                frac_bits += "0"

        posit = "0" + regime + frac_bits
        posit = posit[:32].ljust(32, "0")

    # --- two’s complement for negatives ---
    if neg:
        val = int(posit, 2)
        val = (~val + 1) & 0xFFFFFFFF
        posit = format(val, "032b")

    return posit
#print(int_to_posit32_0(5.757575))

def posit32_to_float(p: str, es: int) -> float:
    """
    Convert posit(32, es) binary string to decimal float.
    Supports es = 0, 1, 2.
    """

    if es not in (0, 1, 2):
        raise ValueError("es must be 0, 1, or 2")

    if len(p) != 32 or any(c not in "01" for c in p):
        raise ValueError("Input must be a 32-bit binary string")

    # Zero
    if p == "0" * 32:
        return 0.0

    # --- sign / two's complement ---
    neg = p[0] == "1"
    if neg:
        val = int(p, 2)
        val = (~val + 1) & 0xFFFFFFFF
        p = format(val, "032b")

    useed = 2 ** (2 ** es)

    # --- regime ---
    i = 1
    regime_bit = p[i]
    run = 0

    while i < 32 and p[i] == regime_bit:
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
    if es > 0 and i + es <= 32:
        exp = int(p[i:i+es], 2)
        i += es

    # --- fraction ---
    frac = 0.0
    scale = 0.5
    while i < 32:
        if p[i] == "1":
            frac += scale
        scale /= 2
        i += 1

    value = (useed ** k) * (2 ** exp) * (1 + frac)

    return -value if neg else value
#print(posit32_to_float("10101100011111000001111100100001",1))

def decode_posit32(p: int, es: int):
    # 1. Handle Special Cases
    if p == 0:
        return 0, 0, 0        # Zero
    if p == 0x80000000:
        return None, None, None  # NaR (Not a Real) / Infinity

    # 2. Decode Sign & 2's Complement
    neg = (p & 0x80000000) != 0
    if neg:
        p = (~p + 1) & 0xFFFFFFFF

    # 3. Decode Regime
    i = 30
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

    # Normalize to Q1.32 (1.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
    mantissa = (1 << 32) | (frac << (32 - frac_len))

    return (-1 if neg else 1), scale, mantissa


def encode_posit32(sign, scale, mantissa, es):
    if mantissa == 0:
        return 0

    # normalize mantissa (keep top bit at position 30)
    while mantissa >= (1 << 31):
        mantissa >>= 1
        scale += 1

    while mantissa < (1 << 30):
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

    # 30 fraction bits for posit32
    frac_bits = format(mantissa & ((1 << 30) - 1), '030b')

    posit_bits = regime_bits + exp_bits + frac_bits

    # 31 bits payload (no sign bit included here)
    posit_bits = posit_bits[:31].ljust(31, '0')

    posit = int(posit_bits, 2)

    if sign < 0:
        posit = (~posit + 1) & 0xFFFFFFFF

    return posit


