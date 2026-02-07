from arithmetics import basic_functions

fn=basic_functions("posit")

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
        - power(a, 19) * 8.22063524662433e-18
        + power(a, 21) * 1.9572941063391263e-20
        - power(a, 23) * 3.868170170630684e-23
        + power(a, 25) * 6.446950284384473e-26
        - power(a, 27) * 9.183689863795546e-29
        + power(a, 29) * 1.1309962886447717e-31
    )



    
