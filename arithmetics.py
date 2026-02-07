import float16 as fp
import posit16 as ps

class basic_functions:
    def __init__(self,type1):
        if type1=="posit":
            a=1
        elif type1=="float":
            a=0
        else:
            print("Enter a valid number system")
        self.type=a
    
    def mul(self,a,b,es):
        if self.type==1:
            return ps.mul(a,b,es)
        elif self.type==0:
            return fp.mul(a,b)
        else:
            return BrokenPipeError
    
    def add(self,a,b):
        if self.type==1:
            return ps.add(a,b)
        elif self.type==0:
            return fp.add(a,b)
        else:
            return BrokenPipeError 
    