import NewFunctions as nf
import math

# nf.mode()

def benchmarks(data_string,type):
    nf.set_number_system(type)
    # Testing Data
    data = data_string
    print(f"Original data: {data}")
    print(f"Relu:{relu_list(data)}")
    print(f"Leaky Relu:{leaky_relu_list(data)}")
    print(f"Softmax:{softmax(data)}")
    print(f"Exponential:{exponential(data)}")
    print(f"Logistic Sigmoid:{logistic_sigmoid(data)}")
    print(f"Hard Sigmoid:{hard_sigmoid(data)}")
    print(f"Softstep:{softstep(data)}")
    print(f"Hard tanh:{hard_tanh(data)}")
    print(f"Swish:{swish(data)}")


def relu_list(arr):
    out = []
    for x in arr:
        out.append(x if x> 0 else 0)
    return out

def leaky_relu_list(arr, alpha=0.01):
    out = []
    for x in arr:
        out.append(x if x >= 0 else nf.mul(alpha,x))
    return out

def softmax(arr):
    # Numerical stability: subtract max
    m = max(arr)
    exp_vals = []
    for x in arr:
        exp_vals.append(nf.exp(x - m))
        #print(nf.exp(x-m))
    s=0
    for a in exp_vals:
        s=nf.add(s,a)
    # s = sum(exp_vals)
    out = []
    for e in exp_vals:
        out.append(nf.div(e, s))
    return out

def exponential(arr):
    out = []
    for x in arr:
        out.append(nf.exp(x))
    return out

def logistic_sigmoid(arr):
    out = []
    for x in arr:
        out.append(nf.div(1.0, (1.0 + nf.exp(-x))))
    return out

def hard_sigmoid(arr):
    out = []
    for x in arr:
        y = nf.add(nf.mul(0.2,x),0.5)
        if y < 0:
            y = 0.0
        elif y > 1:
            y = 1.0
        out.append(y)
    return out

def softstep(arr):
    out = []
    for x in arr:
        out.append(nf.div(1.0, nf.add(1.0, nf.exp(-x))))
    return out

def hard_tanh(arr):
    out = []
    for x in arr:
        if x < -1:
            out.append(-1.0)
        elif x > 1:
            out.append(1.0)
        else:
            out.append(x)
    return out

def swish(arr):
    out = []
    for x in arr:
        sig = nf.div(1.0, nf.add(1 ,nf.exp(-x)))
        out.append(nf.mul(x, sig))
    return out


# print(nf.log(2,10))
# print(nf.ln(10))
# print(nf.reciprocal(0.1))