import random
from sklearn.datasets import fetch_openml
from tqdm import tqdm
import firstlayer as fl
import NewFunctions as nf


# -----------------------------
# Initialize arithmetic backend
# -----------------------------
nf.set_number_system("float16")  # or "posit"
nf.mode()

# -----------------------------
# Load MNIST
# -----------------------------
print("Downloading MNIST (first time only)...")

mnist = fetch_openml("mnist_784", version=1, as_frame=False)

X = mnist.data.astype(float) / 255.0
y = mnist.target.astype(int)

X_train = X[:60000]
y_train = y[:60000]

X_test = X[60000:]
y_test = y[60000:]

print("Dataset loaded!")


# -----------------------------
# Initialize weights
# -----------------------------
def init_weights():
    W = []
    for i in range(10):
        row = []
        for j in range(784):
            row.append(random.uniform(-0.01, 0.01))
        W.append(row)

    b = [0.0 for _ in range(10)]
    return W, b


# -----------------------------
# One-hot encoding
# -----------------------------
def one_hot(label):
    vec = [0.0] * 10
    vec[label] = 1.0
    return vec


# -----------------------------
# Training
# -----------------------------
W, b = init_weights()
lr = 0.01
epochs = 3

print("Starting training...\n")

for epoch in range(epochs):

    total_loss = 0.0

    progress = tqdm(
        zip(X_train[:1000], y_train[:1000]),
        total=1000,
        desc=f"Epoch {epoch+1}"
    )

    for img, label in progress:

        target = one_hot(label)

        W, b, loss = fl.train_step(W, b, img, target, lr)

        total_loss += loss

        progress.set_postfix(loss=loss)

    print(f"Epoch {epoch+1} Total Loss: {total_loss}\n")


# -----------------------------
# Testing
# -----------------------------
print("Evaluating...\n")

correct = 0

progress = tqdm(zip(X_test[:1000], y_test[:1000]), total=1000)

for img, label in progress:

    pred = fl.classifier(W, img, b)

    predicted_class = pred.index(max(pred))

    if predicted_class == label:
        correct += 1

accuracy = correct / 1000
print("\nTest Accuracy:", accuracy)
