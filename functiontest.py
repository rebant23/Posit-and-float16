import float16 as fp


#print(fp.ieee754_16_to_number(fp.to_ieee754_float16(0)))
num1=5.75
num2=2.25

b1="1"
b2="101"

a=fp.decimal_to_ieee(num1)
b=fp.decimal_to_ieee(num2)
c = fp.add_ieee(a, b)
d=fp.mul_ieee(a,b)
# print(binary_multiplier("1011", "1"))

print(f"{num1}+{num2}={fp.ieee_to_decimal(c)}")
print(f"{num1}*{num2}={fp.ieee_to_decimal(d)}")
#print(fp.ieee)