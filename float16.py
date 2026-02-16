import math


def decimal_to_ieee(x):
# def to_ieee754_float16(x):
    #decimal to ieee
    # Handle zero
    if abs(x)< 0.002:
        return "0" * 16
    elif math.isinf(x):
        return "1"*16
    elif math.isnan(x):
        return "0" * (BIAS+1)

    else:
        # Sign bit
        sign = 0
        if x < 0:
            sign = 1
            x = abs(x)

        # Constants for float16
        EXP_BITS = 5
        MAN_BITS = 10
        BIAS = 15

        # Find exponent
        # print(f"number={x}")
        exponent = int(math.floor(math.log2(x)))
        # print(f"exponent={exponent}")
        normalized = x / (2 ** exponent)  # in [1,2)

        # Mantissa (remove leading 1)
        frac = normalized - 1

        mantissa = ""
        for _ in range(MAN_BITS):
            frac *= 2
            if frac >= 1:
                mantissa += "1"
                frac -= 1
            else:
                mantissa += "0"

        # Biased exponent
        exp = exponent + BIAS

        # Overflow / underflow handling (simple)
        if exp <= 0:
            return "0" * 16      # underflow → zero
        if exp >= 31:
            return f"{sign}11111" + "0"*10   # overflow → infinity

        exponent_bits = format(exp, "05b")

        return f"{sign}{exponent_bits}{mantissa}"



def ieee_to_decimal(bits):
#def ieee754_16_to_number(bits):
#convert ieee to integer

    BIAS = 15

    # Extract fields
    sign = int(bits[0])
    exponent = int(bits[1:6], 2)
    mantissa = int(bits[6:], 2)

    # Zero
    if exponent == 0 and mantissa == 0:
        return 0.0

    # Infinity / NaN (basic handling)
    if exponent == 31:
        return float('inf') if mantissa == 0 else float('nan')

    # Normalized number
    exponent -= BIAS

    # Restore hidden 1
    mantissa_val = 1.0

    for i in range(10):
        if (mantissa >> (9 - i)) & 1:
            mantissa_val += 2 ** (-(i + 1))

    value = mantissa_val * (2 ** exponent)

    if sign:
        value = -value

    return value

def add_ieee(a, b):
#add 2 ieee754 numbers

    BIAS = 15

    def decode(x):
        s = int(x[0])
        e = int(x[1:6], 2) - BIAS
        m = int(x[6:], 2) | (1 << 10)   # restore hidden 1
        return s, e, m

    # Decode both numbers
    s1, e1, m1 = decode(a)
    s2, e2, m2 = decode(b)

    # Align exponents
    if e1 > e2:
        m2 >>= (e1 - e2)
        exp = e1
    else:
        m1 >>= (e2 - e1)
        exp = e2

    # Apply sign
    if s1: m1 = -m1
    if s2: m2 = -m2

    # Add mantissas
    mant = m1 + m2

    if mant == 0:
        return "0" * 16

    # Result sign
    sign = 0
    if mant < 0:
        sign = 1
        mant = abs(mant)

    # Normalize
    while mant >= (1 << 11):
        mant >>= 1
        exp += 1

    while mant < (1 << 10):
        mant <<= 1
        exp -= 1

    # Re-bias exponent
    exp += BIAS

    # Overflow / underflow
    if exp <= 0:
        return "0" * 16

    if exp >= 31:
        return f"{sign}11111" + "0"*10

    # Remove hidden bit
    mant &= (1 << 10) - 1

    return f"{sign}{format(exp,'05b')}{format(mant,'010b')}"


def binary_multiplier(a, b):
    # Binary adder
    def bin_add(x, y):
        x = x.zfill(len(y))
        y = y.zfill(len(x))

        carry = 0
        result = ""

        for i in range(len(x)-1, -1, -1):
            s = carry + (x[i] == "1") + (y[i] == "1")
            result = ("1" if s & 1 else "0") + result
            carry = 1 if s > 1 else 0

        if carry:
            result = "1" + result

        return result.lstrip("0") or "0"

    # Shift-and-add multiply
    result = "0"
    b_rev = b[::-1]

    for i, bit in enumerate(b_rev):
        if bit == "1":
            shifted = a + "0"*i
            result = bin_add(result, shifted)

    return result


def binary_to_ieee(bits):
    """
    Encode a binary string (like '101.11' or '-10.01') into IEEE754 FP16.
    Returns 16-bit binary STRING.
    """

    #convert binary to ieee standard

    bias = 15

    # ---------------------------
    # Handle sign
    # ---------------------------
    sign = 0
    if bits[0] == "-":
        sign = 1
        bits = bits[1:]

    if "." not in bits:
        bits += ".0"

    int_part, frac_part = bits.split(".")

    # Remove leading zeros
    int_part = int_part.lstrip("0") or "0"

    # Zero case
    if int_part == "0" and set(frac_part) == {"0"}:
        return "0" * 16

    # ---------------------------
    # Normalize
    # ---------------------------
    if int_part != "0":
        shift = len(int_part) - 1
        mantissa_bits = int_part[1:] + frac_part
    else:
        first_one = frac_part.find("1")
        shift = -(first_one + 1)
        mantissa_bits = frac_part[first_one + 1:]

    exponent = shift + bias

    # ---------------------------
    # Fraction (10 bits)
    # ---------------------------
    mantissa_bits += "0" * 20
    fraction = mantissa_bits[:10]

    # ---------------------------
    # Assemble fields
    # ---------------------------
    exp_bits = format(exponent, "05b")

    return str(sign) + exp_bits + fraction

def float_to_fp16_binary(x):
    """
    Convert Python float to IEEE754 FP16 binary string.
    Returns 16-bit string.
    """

    # Special cases
    if math.isnan(x):
        return "0111110000000001"
    if math.isinf(x):
        return "1111110000000000" if x < 0 else "0111110000000000"
    if x == 0.0:
        return "1" + "0"*15 if math.copysign(1, x) < 0 else "0"*16

    sign = 0
    if x < 0:
        sign = 1
        x = -x

    bias = 15

    # Normalize
    exp = int(math.floor(math.log(x, 2)))
    mant = x / (2 ** exp)

    # Handle subnormals
    if exp + bias <= 0:
        frac = int(x / (2 ** (-14)) * (2 ** 10))
        return str(sign) + "00000" + format(frac, "010b")

    exponent = exp + bias

    # Mantissa (remove implicit 1)
    mant -= 1.0
    frac = int(round(mant * (2 ** 10)))

    # Handle rounding overflow
    if frac == (1 << 10):
        frac = 0
        exponent += 1

    # Overflow → infinity
    if exponent >= 31:
        return str(sign) + "11111" + "0"*10

    return (
        str(sign)
        + format(exponent, "05b")
        + format(frac, "010b")
    )


def fp16_to_binary_string(fp):
    """
    Convert IEEE754 FP16 binary string to standard binary string.
    Example:
        "0100000010110000" -> "101.11"
    """

    assert len(fp) == 16 and set(fp) <= {"0", "1"}

    sign = fp[0]
    exponent = int(fp[1:6], 2)
    fraction = fp[6:]

    bias = 15

    # Special cases
    if exponent == 31:
        return "-inf" if sign == "1" else "inf"

    if exponent == 0 and set(fraction) == {"0"}:
        return "-0" if sign == "1" else "0"

    # Build mantissa
    if exponent == 0:
        mantissa = "0." + fraction
        shift = 1 - bias
    else:
        mantissa = "1." + fraction
        shift = exponent - bias

    bits = mantissa.replace(".", "")

    # Shift binary point
    if shift >= 0:
        point = 1 + shift
    else:
        point = len(bits) + shift

    # Pad if needed
    if point >= len(bits):
        bits += "0" * (point - len(bits))
    elif point <= 0:
        bits = "0" * (-point) + bits
        point = 0

    result = bits[:point] + "." + bits[point:]

    # Cleanup
    result = result.rstrip("0").rstrip(".")
    if result.startswith("."):
        result = "0" + result
    if sign == "1":
        result = "-" + result

    return result

def mul_ieee(a, b):
    assert len(a) == 16 and len(b) == 16

    bias = 15

    sa, ea, fa = int(a[0]), int(a[1:6], 2), int(a[6:], 2)
    sb, eb, fb = int(b[0]), int(b[1:6], 2), int(b[6:], 2)

    # Zero shortcut
    if (ea == 0 and fa == 0) or (eb == 0 and fb == 0):
        return "0" * 16

    # Sign
    sign = sa ^ sb

    # Restore mantissas (11 bits)
    ma = (1 << 10) | fa
    mb = (1 << 10) | fb

    # Exponent
    exp = ea + eb - bias

    # Multiply (22 bits)
    prod = ma * mb

    # Normalize
    if prod & (1 << 21):
        shift = 11
        exp += 1
    else:
        shift = 10

    # Extract with guard/round/sticky
    mant = prod >> shift
    remainder = prod & ((1 << shift) - 1)

    guard = (remainder >> (shift - 1)) & 1
    round_bit = (remainder >> (shift - 2)) & 1 if shift >= 2 else 0
    sticky = 1 if (remainder & ((1 << (shift - 2)) - 1)) else 0

    # Round to nearest
    if guard and (round_bit or sticky or (mant & 1)):
        mant += 1

    # Mantissa overflow after rounding
    if mant == (1 << 11):
        mant >>= 1
        exp += 1

    frac = mant & 0x3FF

    # Overflow
    if exp >= 31:
        return str(sign) + "11111" + "0" * 10

    # Underflow (simple flush to zero)
    if exp <= 0:
        return "0" * 16

    return str(sign) + format(exp, "05b") + format(frac, "010b")


def mul(num1,num2):
    a=decimal_to_ieee(num1)
    b=decimal_to_ieee(num2)
    return float(ieee_to_decimal(mul_ieee(a,b)))

def add(num1,num2):
    a=decimal_to_ieee(num1)
    b=decimal_to_ieee(num2)
    return float(ieee_to_decimal(add_ieee(a,b)))