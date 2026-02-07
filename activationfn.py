import NewFunctions as nf
import float16 as fp

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

import math

def softmax(arr):
    # subtract max for numerical stability
    m = max(arr)
    exp_vals = []
    for x in arr:
        exp_vals.append(nf.exp(x - m))
    s = sum(exp_vals)
    out = []
    for e in exp_vals:
        out.append(e / s)
    return out






data = [-3, -1, 0, 2, 5]
print(f"Original data: {data}")
print(f"Relu:{relu_list(data)}")
print(f"Relu:{leaky_relu_list(data)}")
print(f"Softmax:{softmax(data)}")
