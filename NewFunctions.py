from arithmetics import basic_functions


GLOBAL_STR = "float16"

def set_number_system(s):
    global GLOBAL_STR
    global fn
    GLOBAL_STR = s
    fn=basic_functions(GLOBAL_STR)
# print(fn.mul(5.75,2.25))
# print(fn.add(5.75,2.25))

def mode():
    print(f"Selected mode: {GLOBAL_STR}")

def mul(a,b,es=2):
    global fn
    return fn.mul(a,b,es)

def add(a,b,es=2):
    global fn
    return fn.add(a,b,es)

def power(a, b):
    result = 1.0
    for _ in range(abs(b)):
        result = mul(result, a)
    return result

def sin(a):
    return  add(
                        add(
                            add(
                                add(
                                    mul(power(a, 1), 1.0),
                                    mul(power(a, 3), -0.16666666666666666)
                                ),
                                mul(power(a, 5), 0.008333333333333333)
                            ),
                            mul(power(a, 7), -0.0001984126984126984)
                        ),
                        mul(power(a, 9), 2.7557319223985893e-06)
                    )
#print(sin(1))
def exp_taylor(a):
    return add(
        add(
            add(
                add(
                    add(
                        add(
                            add(
                                add(
                                    add(
                                        mul(power(a, 1), 1.0),
                                        1.0
                                    ),
                                    mul(power(a, 2), 0.5)
                                ),
                                mul(power(a, 3), 0.16666666666666666)
                            ),
                            mul(power(a, 4), 0.041666666666666664)
                        ),
                        mul(power(a, 5), 0.008333333333333333)
                    ),
                    mul(power(a, 6), 0.001388888888888889)
                ),
                mul(power(a, 7), 0.0001984126984126984)
            ),
            mul(power(a, 8), 2.48015873015873e-05)
        ),
        0.0
    )

def exp(a):
    b = mul(a, 0.25)      # a / 4
    t = exp_taylor(b)
    t = mul(t, t)
    t = mul(t, t)         # (e^(a/4))^4
    return t


def reciprocal(x, iterations=6):
    # crude initial guess (works for x near 1–10)
    # y =0.1**(math.floor(math.log10(abs(x)))+1)
    y=power(0.1,len(str(int(abs(x)))))
    #1^-(number of digits in x)
    for _ in range(iterations):
        y = mul(y,add(2.0,mul(-1, mul(abs(x), y))))
    if x>=0:
        sign=1
    else:
        sign=-1
    if abs(x)>=1:
        return mul(y,sign)
    else:
        return mul(reciprocal(mul(10,x)),10)

def div(x,y):
    return mul(x,reciprocal(y))

def ln(x):
    LN2 = 0.6931471805599453
    if x <= 0:
        raise ValueError("x must be positive")

    # Range reduction: x = m * 2^k
    k = 0
    while x > 1.5:
        x = mul(x, 0.5)
        k = add(k,1)

    while x < 0.75:
        x = mul(x, 2.0)
        k = add(k,-1)

    # Polynomial ln(1+z)
    z = add(x, -1.0)

    z2 = mul(z, z)
    z3 = mul(z2, z)
    z4 = mul(z3, z)

    # Pre-divided constants
    t1 = z
    t2 = mul(z2, -0.5)
    t3 = mul(z3, 0.3333333333333333)
    t4 = mul(z4, -0.25)

    ln_m = add(add(t1, t2), add(t3, t4))

    return add(ln_m, mul(float(k), LN2))

def log(a,b):
    #b is base
    return div(ln(a),ln(b))


def dot(a, b, es=2):
    if len(a) != len(b):
        raise ValueError("Vectors must have same length")

    result = 0.0
    for x, y in zip(a, b):
        result = add(result, mul(x, y, es), es)

    return result

def matvec(W, x):
    out = []
    for row in W:
        out.append(dot(row, x))
    return out

# W = [
#     [0.5, -1.0, 0.3],
#     [0.8, 0.2, -0.6]
# ]

# x = [1.0, 2.0, -1.0]

# print(matvec(W, x))

def vector_add(a, b):
    if len(a) != len(b):
        raise ValueError("Vectors must have same length")

    return [add(x, y) for x, y in zip(a, b)]
