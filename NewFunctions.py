from arithmetics import basic_functions

fn=basic_functions("float")

# print(fn.mul(5.75,2.25))
# print(fn.add(5.75,2.25))

def mul(a,b):
    return fn.mul(a,b)

def add(a,b):
    return fn.add(a,b)

def power(a, b):
    result = 1.0
    for _ in range(b):
        result = fn.mul(result, a)
    return result

def sin(a):
    return (
        power(a, 1)  * 1.0
        - power(a, 3)  * 0.16666666666666666
        + power(a, 5)  * 0.008333333333333333
        - power(a, 7)  * 0.0001984126984126984
        + power(a, 9)  * 2.7557319223985893e-06
        - power(a, 11) * 2.505210838544172e-08
        + power(a, 13) * 1.6059043836821613e-10
        - power(a, 15) * 7.647163731819816e-13
        + power(a, 17) * 2.8114572543455206e-15
    )
print(sin(1))
def exp(a):
    return (
        1.0
        + mul(power(a, 1), 1.0)
        + mul(power(a, 2), 0.5)
        + mul(power(a, 3), 0.16666666666666666)
        + mul(power(a, 4), 0.041666666666666664)
        + mul(power(a, 5), 0.008333333333333333)
        + mul(power(a, 6), 0.001388888888888889)
        + mul(power(a, 7), 0.0001984126984126984)
        + mul(power(a, 8), 2.48015873015873e-05)
        + mul(power(a, 9), 2.7557319223985893e-06)
        + mul(power(a, 10), 2.755731922398589e-07)
        + mul(power(a, 11), 2.505210838544172e-08)
        + mul(power(a, 12), 2.08767569878681e-09)
        + mul(power(a, 13), 1.6059043836821613e-10)
        + mul(power(a, 14), 1.1470745597729725e-11)
    )


    
