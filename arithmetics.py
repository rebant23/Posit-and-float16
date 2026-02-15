import float16 as fp
import posit16 as ps16
import posit32 as ps32
import posit8 as ps8
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
        else:
            return a+b
    