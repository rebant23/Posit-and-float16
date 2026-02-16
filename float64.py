# 8 bit standard used: | sign (1) | exponent (11) | fraction (52) |
import math

#change line 212, return formats and constants to convert to other formats

def decimal_to_ieee(x):
# def to_ieee754_float16(x):
    #decimal to ieee
    # Handle zero
     # Constants for float16
    EXP_BITS = 11
    MAN_BITS = 52
    BIAS = 1023

    if x==0:
        return "0" * (BIAS+1)
    elif math.isinf(x):
        return "1"*(BIAS+1)

    else:
        # Sign bit
        sign = 0
        if x < 0:
            sign = 1
            x = abs(x)


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
            return "0" * (BIAS+1)      # underflow → zero
        if exp >= (2*BIAS+1):
            return f"{sign}"+"1"*EXP_BITS + "0"*(MAN_BITS)   # overflow → infinity

        exponent_bits = format(exp, "011b")

        return f"{sign}{exponent_bits}{mantissa}"

def ieee_to_decimal(bits):
#def ieee754_16_to_number(bits):
#convert ieee to integer

    BIAS = 1023
    EXP_BITS = 11
    MAN_BITS = 52
       
    # Extract fields
    sign = int(bits[0])
    exponent = int(bits[1:(EXP_BITS+1)], 2)
    mantissa = int(bits[(EXP_BITS+1):], 2)

    # Zero
    if exponent == 0 and mantissa == 0:
        return 0.0

    # Infinity / NaN (basic handling)
    if exponent == (2**EXP_BITS-1):
        return float('inf') if mantissa == 0 else float('nan')

    # Normalized number
    exponent -= BIAS

    # Restore hidden 1
    mantissa_val = 1.0

    for i in range(MAN_BITS):
        if (mantissa >> ((MAN_BITS-1) - i)) & 1:
            mantissa_val += 2 ** (-(i + 1))
    value = mantissa_val * (2 ** exponent)

    if sign:
        value = -value

    return value

def add_ieee(a, b):
#add 2 ieee754 numbers

    BIAS = 1023
    EXP_BITS = 11
    MAN_BITS = 52

    def decode(x):
        s = int(x[0])
        e = int(x[1:(EXP_BITS+1)], 2) - BIAS
        m = int(x[(EXP_BITS+1):], 2) | (1 << (MAN_BITS))   # restore hidden 1
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
        return "0" * (BIAS+1)

    # Result sign
    sign = 0
    if mant < 0:
        sign = 1
        mant = abs(mant)

    # Normalize
    while mant >= (1 << (MAN_BITS+1)):
        mant >>= 1
        exp += 1

    while mant < (1 << (MAN_BITS)):
        mant <<= 1
        exp -= 1

    # Re-bias exponent
    exp += BIAS

    # Overflow / underflow
    if exp <= 0:
        return "0" * (BIAS+1)

    if exp >= (2**EXP_BITS-1):
        return f"{sign}"+"1"*EXP_BITS + "0"*(MAN_BITS)

    # Remove hidden bit
    mant &= (1 << (MAN_BITS)) - 1

    return f"{sign}{format(exp,'011b')}{format(mant,'052b')}"

def mul_ieee(a, b):

    BIAS = 1023
    EXP_BITS = 11
    MAN_BITS = 52

    # assert len(a) == (BIAS+1) and len(b) == (BIAS+1)

    sa, ea, fa = int(a[0]), int(a[1:(EXP_BITS+1)], 2), int(a[(EXP_BITS+1):], 2)
    sb, eb, fb = int(b[0]), int(b[1:(EXP_BITS+1)], 2), int(b[(EXP_BITS+1):], 2)

    # Zero shortcut
    if (ea == 0 and fa == 0) or (eb == 0 and fb == 0):
        return "0" * (BIAS+1)

    # Sign
    sign = sa ^ sb

    # Restore mantissas (4 bits)
    ma = (1 << (MAN_BITS)) | fa
    mb = (1 << (MAN_BITS)) | fb

    # Exponent
    exp = ea + eb - BIAS

    # Multiply (8 bits)
    prod = ma * mb

    # Normalize
    if prod & (1 << (MAN_BITS*2+1)):
        shift = (MAN_BITS+1)
        exp += 1
    else:
        shift = (MAN_BITS)

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
    if mant == (1 << (MAN_BITS+1)):
        mant >>= 1
        exp += 1

    frac = mant & 0xFFFFFFFFFFFFF

    # Overflow
    if exp >= (2**EXP_BITS-1):
        return str(sign) + "1"*(EXP_BITS) + "0" * (MAN_BITS)

    # Underflow (simple flush to zero)
    if exp <= 0:
        return "0" * (BIAS+1)

    return str(sign) + format(exp, "011b") + format(frac, "52b")


def mul(num1,num2):
    a=decimal_to_ieee(num1)
    b=decimal_to_ieee(num2)
    return float(ieee_to_decimal(mul_ieee(a,b)))

def add(num1,num2):
    a=decimal_to_ieee(num1)
    b=decimal_to_ieee(num2)
    return float(ieee_to_decimal(add_ieee(a,b)))

print(ieee_to_decimal(decimal_to_ieee(10)))
print(ieee_to_decimal(mul_ieee(decimal_to_ieee(5.75),decimal_to_ieee(0.25))))
print(ieee_to_decimal(add_ieee(decimal_to_ieee(5.3425),decimal_to_ieee(2.654))))