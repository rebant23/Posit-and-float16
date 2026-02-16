import NewFunctions as nf
import activationfn as af


def first_layer(W, x, b):
    # Linear transformation
    z = nf.matvec(W, x)

    # Add bias
    z = nf.vector_add(z, b)

    # Softmax activation
    return af.softmax(z)
def flatten(x):
    flat = []
    for sub in x:
        if isinstance(sub, list):
            for item in sub:
                if isinstance(item, list):
                    flat.extend(item)
                else:
                    flat.append(item)
        else:
            flat.append(sub)
    return flat
def classifier(W, x, b):
    x = flatten(x)
    return first_layer(W, x, b)
