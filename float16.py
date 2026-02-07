import math

def to_ieee754_float16(x):
    # Handle zero
    if x == 0:
        return "0" * 16

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
    exponent = int(math.floor(math.log2(x)))
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

def ieee754_16_to_number(bits):
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

def add_ieee754_16(a, b):
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


def binary_multiplier(a, b):

    # Binary adder (string-based)
    def bin_add(x, y):
        x = x.zfill(len(y))
        y = y.zfill(len(x))

        carry = 0
        result = ""

        for i in range(len(x) - 1, -1, -1):
            s = carry + (x[i] == "1") + (y[i] == "1")
            result = ("1" if s & 1 else "0") + result
            carry = 1 if s > 1 else 0

        if carry:
            result = "1" + result

        return result.lstrip("0") or "0"

    # Shift-and-add multiplication
    result = "0"
    b_rev = b[::-1]

    for i, bit in enumerate(b_rev):
        if bit == "1":
            shifted = a + "0" * i
            result = bin_add(result, shifted)

    return result



# print(ieee754_16_to_number(to_ieee754_float16(0)))
num1=5.75
num2=2.25

b1="1"
b2="101"

a=to_ieee754_float16(num1)
b=to_ieee754_float16(num2)
c = add_ieee754_16(a, b)

print(binary_multiplier("1011", "1"))

print(f"{num1}+{num2}={ieee754_16_to_number(c)}")
#print(f"{num1}*{num2}={ieee754_16_to_number(d)}")
