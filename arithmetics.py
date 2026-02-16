import float16 as fp
import float8 as fp8
import float32 as fp32
import float64 as fp64
import posit16 as ps16
import posit32 as ps32
import posit8 as ps8
import posit64 as ps64
import math

class basic_functions:
    def __init__(self,type1):
        if type1=="posit16":
            a=1
        elif type1=="float":
            a=0
        elif type1=="math":
            a=2
        elif type1=="posit32":
            a=3
        elif type1=="posit8":
            a=4
        elif type1=="posit64":
            a=5
        elif type1=="float8":
            a=6
        elif type1=="float32":
            a=7
        elif type1=="float64":
            a=8
        else:
            print("Enter a valid number system")
        self.type=a
    
    def mul(self,a,b,es):
        if self.type==1:
            return ps16.mul(a,b,es)
        elif self.type==0:
            return fp.mul(a,b)
        elif self.type==2:
            return a*b
        elif self.type==3:
            return ps32.mul(a,b,es)
        elif self.type==4:
            return ps8.mul(a,b,es)
        elif self.type==5:
            return ps64.mul(a,b,es)
        elif self.type==6:
            return fp8.mul(a,b)
        elif self.type==7:
            return fp32.mul(a,b)
        elif self.type==8:
            return fp64.mul(a,b)
        else:
            return a*b
    
    def add(self,a,b,es):
        if self.type==1:
            return ps16.add(a,b,es)
        elif self.type==0:
            return fp.add(a,b)
        elif self.type==2:
            return a+b
        elif self.type==3:
            return ps32.add(a,b,es)
        elif self.type==4:
            return ps8.add(a,b,es)
        elif self.type==5:
            return ps64.add(a,b,es)
        elif self.type==6:
            return fp8.add(a,b)
        elif self.type==7:
            return fp32.add(a,b)
        elif self.type==8:
            return fp64.add(a,b)
        else:
            return a+b
    