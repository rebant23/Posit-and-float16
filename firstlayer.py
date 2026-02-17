import NewFunctions as nf
import activationfn as af

# ----------------- Forward -----------------

def first_layer(W, x, b):
    """
    Computes the first layer output: z = Wx + b, then applies softmax
    """
    z = nf.matvec(W, x)
    z = nf.vector_add(z, b)
    return af.softmax(z)


def flatten(x):
    """
    Flattens a nested list into a single list
    """
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
    """
    Flattens input and applies first_layer
    """
    x = flatten(x)
    return first_layer(W, x, b)


# ----------------- Loss -----------------

def cross_entropy(pred, target, epsilon=1e-3):
    """
    Computes cross-entropy loss safely by ensuring predictions are positive
    """
    loss = 0.0

    # Clip predictions to ensure strictly positive values
    pred_clipped = [max(p, epsilon) for p in pred]

    for p, t in zip(pred_clipped, target):
        if t == 1.0:
            loss = nf.add(loss, -nf.ln(p))

    return loss


# ----------------- Gradients -----------------

def compute_gradients(pred, target, x):
    """
    Computes gradients of loss w.r.t W and b
    """
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
    """
    Updates weights and biases using gradient descent
    """
    for i in range(len(W)):
        for j in range(len(W[0])):
            W[i][j] = nf.add(W[i][j], -nf.mul(lr, dW[i][j]))

    for i in range(len(b)):
        b[i] = nf.add(b[i], -nf.mul(lr, dB[i]))

    return W, b


# ----------------- One Training Step -----------------

def train_step(W, b, image, target, lr):
    """
    Performs a single training step:
    - forward pass
    - compute loss
    - compute gradients
    - update parameters
    """
    # Flatten image
    x = flatten(image)

    # Forward pass
    pred = first_layer(W, x, b)

    # Clip predictions to avoid log(0) or negatives
    pred = [max(p, 1e-3) for p in pred]

    # Compute loss
    loss = cross_entropy(pred, target)

    # Compute gradients
    dW, dB = compute_gradients(pred, target, x)

    # Update parameters
    W, b = update_parameters(W, b, dW, dB, lr)

    return W, b, loss
