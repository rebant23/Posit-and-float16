from arithmetics import basic_functions

fn=basic_functions("posit16")

# print(fn.mul(5.75,2.25))
# print(fn.add(5.75,2.25))

def mul(a,b,es=2):
    return fn.mul(a,b,es)

def add(a,b,es=2):
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


#print(exp(-3))
