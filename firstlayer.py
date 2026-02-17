import NewFunctions as nf
import activationfn as af


# ----------------- Forward -----------------

def first_layer(W, x, b):
    z = nf.matvec(W, x)
    z = nf.vector_add(z, b)
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


# ----------------- Loss -----------------

def cross_entropy(pred, target):
    epsilon = 1e-9
    loss = 0.0

    for p, t in zip(pred, target):
        if t == 1.0:
            loss = nf.add(loss, -nf.ln(nf.add(p, epsilon)))

    return loss


# ----------------- Gradients -----------------

def compute_gradients(pred, target, x):
    # dZ = pred - target
    dZ = []
    for p, t in zip(pred, target):
        dZ.append(nf.add(p, -t))

    # dW = outer(dZ, x)
    dW = []
    for dz in dZ:
        row = []
        for xi in x:
            row.append(nf.mul(dz, xi))
        dW.append(row)

    # dB = dZ
    dB = dZ

    return dW, dB


# ----------------- Update -----------------

def update_parameters(W, b, dW, dB, lr):

    for i in range(len(W)):
        for j in range(len(W[0])):
            W[i][j] = nf.add(
                W[i][j],
                -nf.mul(lr, dW[i][j])
            )

    for i in range(len(b)):
        b[i] = nf.add(
            b[i],
            -nf.mul(lr, dB[i])
        )

    return W, b


# ----------------- One Training Step -----------------

def train_step(W, b, image, target, lr):

    x = flatten(image)

    pred = first_layer(W, x, b)

    loss = cross_entropy(pred, target)

    dW, dB = compute_gradients(pred, target, x)

    W, b = update_parameters(W, b, dW, dB, lr)

    return W, b, loss
