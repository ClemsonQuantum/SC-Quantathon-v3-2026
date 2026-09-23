"""Figures and numbers for the Day 7 notes. Run from this folder in the scqv3 env: python make_figures.py

Reproduces the notebook's experiments in the notebook's order with the notebook's seeds, saves vector figures
to figures/, and prints the numbers quoted in notes.tex.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp, Statevector
from sklearn.datasets import make_circles, make_moons
from sklearn.svm import SVC

warnings.filterwarnings("ignore")
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(seed=3)
estimator = StatevectorEstimator()

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
BLUE, ORANGE, GREEN, GRAY = "#1f77b4", "#ff7f0e", "#2ca02c", "0.45"
LIGHT = ["#dbe9f6", "#fde5cc"]


def scale_01(X):
    return (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))


X_circ, y_circ = make_circles(n_samples=120, factor=0.4, noise=0.08, random_state=3)
X_moon, y_moon = make_moons(n_samples=120, noise=0.15, random_state=3)
X_circ, X_moon = scale_01(X_circ), scale_01(X_moon)
y_circ, y_moon = 2 * y_circ - 1, 2 * y_moon - 1
datasets = {"circles": (X_circ, y_circ), "moons": (X_moon, y_moon)}


# Figure 1: the two datasets and the three encodings of one point
def angle_map(x):
    qc = QuantumCircuit(2)
    qc.ry(np.pi * x[0], 0)
    qc.ry(np.pi * x[1], 1)
    return qc


def entangling_map(x):
    qc = QuantumCircuit(2)
    qc.ry(np.pi * x[0], 0)
    qc.ry(np.pi * x[1], 1)
    qc.cx(0, 1)
    qc.ry(np.pi * x[0] * x[1], 1)
    return qc


def zz_map(x, reps=2):
    qc = QuantumCircuit(2)
    for _ in range(reps):
        qc.h([0, 1])
        qc.p(2 * x[0], 0)
        qc.p(2 * x[1], 1)
        qc.cx(0, 1)
        qc.p(2 * (np.pi - x[0]) * (np.pi - x[1]), 1)
        qc.cx(0, 1)
    return qc


feature_map = entangling_map
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3))
for ax, (name, (X, y)) in zip(axes, datasets.items()):
    ax.scatter(*X[y < 0].T, s=16, color=BLUE, label="class $-1$")
    ax.scatter(*X[y > 0].T, s=16, color=ORANGE, label="class $+1$")
    ax.set_title(name)
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")
    ax.set_aspect("equal")
axes[0].legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "datasets.pdf")
plt.close(fig)
x = np.array([3.0, 1.0, 2.0, 4.0])
x_norm = x / np.linalg.norm(x)
print(
    "[1/6] datasets.pdf   amplitude encoding of",
    x,
    "-> probabilities",
    np.round(x_norm**2, 3),
    "; angle map |phi(0.3,0.8)> =",
    np.round(Statevector(angle_map([0.3, 0.8])).data.real, 3),
)
phi_a, phi_b = Statevector(feature_map([0.3, 0.8])), Statevector(feature_map([0.9, 0.1]))
print("      overlap of the two encoded points (entangling map):", round(abs(phi_a.inner(phi_b)) ** 2, 4))
fig = feature_map([0.3, 0.8]).draw("mpl", style="clifford")
fig.savefig(OUT / "feature_map.pdf")
plt.close(fig)


# Figure 2: kernel SVM on both datasets, with the ZZ map for comparison (rng order as in the notebook)
def kernel_matrix(A, B, fmap=feature_map):
    sa = [Statevector(fmap(a)) for a in A]
    sb = [Statevector(fmap(b)) for b in B]
    return np.array([[abs(a.inner(b)) ** 2 for b in sb] for a in sa])


def split(X, y, n_train=80):
    idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:]
    return X[tr], y[tr], X[te], y[te]


def fit_quantum_svm(X_train, y_train, X_test, y_test, fmap=feature_map):
    K_train = kernel_matrix(X_train, X_train, fmap)
    K_test = kernel_matrix(X_test, X_train, fmap)
    clf = SVC(kernel="precomputed", C=1.0).fit(K_train, y_train)
    return clf, clf.score(K_train, y_train), clf.score(K_test, y_test)


splits = {name: split(X, y) for name, (X, y) in datasets.items()}  # one fixed split per dataset, as in the notebook
results = {}
for name in datasets:
    X_train, y_train, X_test, y_test = splits[name]
    _, acc_train, acc_test = fit_quantum_svm(X_train, y_train, X_test, y_test)
    acc_linear = SVC(kernel="linear").fit(X_train, y_train).score(X_test, y_test)
    acc_rbf = SVC(kernel="rbf").fit(X_train, y_train).score(X_test, y_test)
    results[name] = (acc_train, acc_test, acc_linear, acc_rbf)
print("[2/6] kernel_svm.pdf")
for name, (a, b, c, d) in results.items():
    print(f"      {name:<8} quantum kernel train {a:.0%} test {b:.0%} | linear {c:.0%} | RBF {d:.0%}")
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.7))
n_grid = 35
g = np.linspace(0, 1, n_grid)
grid = np.array([[gx, gy] for gy in g for gx in g])
for ax, name in zip(axes, datasets):
    X_train, y_train, X_test, y_test = splits[name]
    clf, _, acc_test = fit_quantum_svm(X_train, y_train, X_test, y_test)
    Z = clf.decision_function(kernel_matrix(grid, X_train)).reshape(n_grid, n_grid)
    ax.contourf(g, g, Z, levels=[-10, 0, 10], colors=LIGHT)
    ax.contour(g, g, Z, levels=[0], colors="0.3", linewidths=1)
    ax.scatter(*X_train[y_train < 0].T, s=14, color=BLUE)
    ax.scatter(*X_train[y_train > 0].T, s=14, color=ORANGE)
    ax.scatter(*X_test.T, s=30, facecolors="none", edgecolors="k", linewidths=0.6)
    ax.set_title(f"{name}: quantum kernel SVM, test {acc_test:.0%}")
    ax.set_aspect("equal")
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")
fig.tight_layout()
fig.savefig(OUT / "kernel_svm.pdf")
plt.close(fig)
zz = {}
for name in datasets:
    X_train, y_train, X_test, y_test = splits[name]
    zz[name] = fit_quantum_svm(X_train, y_train, X_test, y_test, zz_map)[2]
print("      ZZ feature map test accuracy:", {k: f"{v:.0%}" for k, v in zz.items()})

# Figure 3: kernel matrices sorted by class, entangling map against ZZ map
X_train, y_train, X_test, y_test = splits["circles"]
order = np.concatenate([np.where(y_train < 0)[0], np.where(y_train > 0)[0]])
n_neg = int((y_train < 0).sum())  # first n_neg rows of the sorted matrix are class -1
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3))
for ax, fmap, title in zip(axes, [feature_map, zz_map], ["entangling map", "ZZ feature map"]):
    K = kernel_matrix(X_train[order], X_train[order], fmap)
    im = ax.imshow(K, cmap="viridis", vmin=0, vmax=1)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    print(
        f"      {title}: mean off-diagonal kernel {K[~np.eye(len(K), dtype=bool)].mean():.3f}, within-class block means {K[:n_neg, :n_neg].mean():.3f} / {K[n_neg:, n_neg:].mean():.3f}"
    )
fig.colorbar(im, ax=axes, fraction=0.03, label="$k(x_i, x_j)$")
fig.savefig(OUT / "kernel_matrices.pdf")
plt.close(fig)
print("[3/6] kernel_matrices.pdf")

# Figure 4: the variational classifier (same rng order as the notebook: theta0, then three restarts)
x_params = ParameterVector("x", 2)
a_params = ParameterVector("a", 6)


def ansatz(params, reps=2):
    qc = QuantumCircuit(2)
    k = 0
    for layer in range(reps + 1):
        for q in range(2):
            qc.ry(params[k], q)
            k += 1
        if layer < reps:
            qc.cx(0, 1)
    return qc


model_circuit = feature_map(x_params).compose(ansatz(a_params))
observable = SparsePauliOp("IZ")
fig = model_circuit.draw("mpl", style="clifford", fold=-1)
fig.savefig(OUT / "vqc_circuit.pdf")
plt.close(fig)


def model(theta, X):
    values = np.array([np.concatenate([theta, x]) for x in X])
    return np.asarray(estimator.run([(model_circuit, observable, values)]).result()[0].data.evs)


def loss(theta, X, y):
    return float(np.mean((model(theta, X) - y) ** 2))


def model_gradient(theta, X):
    grad = np.zeros((len(X), len(theta)))
    for k in range(len(theta)):
        s = np.zeros(len(theta))
        s[k] = np.pi / 2
        grad[:, k] = 0.5 * (model(theta + s, X) - model(theta - s, X))
    return grad


def loss_gradient(theta, X, y):
    return 2 * np.mean((model(theta, X) - y)[:, None] * model_gradient(theta, X), axis=0)


def accuracy(theta, X, y):
    return np.mean(np.sign(model(theta, X)) == y)


X_train, y_train, X_test, y_test = splits["circles"]
theta0 = rng.uniform(0, 2 * np.pi, 6)
L0 = loss(theta0, X_train, y_train)
G = model_gradient(theta0, X_train[:4])
eps = 1e-5
fd = np.zeros_like(G)
for k in range(6):
    e = np.zeros(6)
    e[k] = eps
    fd[:, k] = (model(theta0 + e, X_train[:4]) - model(theta0 - e, X_train[:4])) / (2 * eps)
print(f"[4/6] vqc.pdf   loss at random angles {L0:.3f}; max |shift - finite difference| = {np.abs(G - fd).max():.1e}")


def train(theta, X, y, steps=60, lr=0.4):
    history = []
    for _ in range(steps):
        theta = theta - lr * loss_gradient(theta, X, y)
        history.append((loss(theta, X, y), accuracy(theta, X, y)))
    return theta, np.array(history)


best = None
for restart in range(3):
    th, hist = train(rng.uniform(0, 2 * np.pi, 6), X_train, y_train)
    print(f"      restart {restart}: final loss {hist[-1, 0]:.3f}, train accuracy {hist[-1, 1]:.0%}")
    if best is None or hist[-1, 0] < best[1][-1, 0]:
        best = (th, hist)
theta_best, history = best
acc_test = accuracy(theta_best, X_test, y_test)
print(
    f"      best restart: train {history[-1, 1]:.0%}, test {acc_test:.0%}; loss after 1, 10, 60 steps: {history[0, 0]:.3f}, {history[9, 0]:.3f}, {history[-1, 0]:.3f}"
)
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.3), gridspec_kw={"width_ratios": [1.15, 1]})
ax1 = axes[0]
ax1.plot(history[:, 0], color=BLUE)
ax1.set_xlabel("gradient step")
ax1.set_ylabel("loss", color=BLUE)
ax2 = ax1.twinx()
ax2.plot(history[:, 1], color=ORANGE)
ax2.set_ylabel("training accuracy", color=ORANGE)
ax2.set_ylim(0, 1.05)
ax2.spines["top"].set_visible(False)
ax1.set_title("training on the circles data")
Z = model(theta_best, grid).reshape(n_grid, n_grid)
axes[1].contourf(g, g, Z, levels=[-2, 0, 2], colors=LIGHT)
axes[1].contour(g, g, Z, levels=[0], colors="0.3", linewidths=1)
axes[1].scatter(*X_train[y_train < 0].T, s=14, color=BLUE)
axes[1].scatter(*X_train[y_train > 0].T, s=14, color=ORANGE)
axes[1].scatter(*X_test.T, s=30, facecolors="none", edgecolors="k", linewidths=0.6)
axes[1].set_aspect("equal")
axes[1].set_xlabel("feature 1")
axes[1].set_ylabel("feature 2")
axes[1].set_title(f"sign of $f(x;\\theta)$, test {acc_test:.0%}")
fig.tight_layout()
fig.savefig(OUT / "vqc.pdf")
plt.close(fig)


# Figure 5: barren plateaus (same order as the notebook: widths 2, 3, 5, 6, 8, then 4)
def wide_ansatz(n, reps):
    params = ParameterVector("t", n * (reps + 1))
    qc = QuantumCircuit(n)
    k = 0
    for layer in range(reps + 1):
        for q in range(n):
            qc.ry(params[k], q)
            k += 1
        if layer < reps:
            for q in range(n - 1):
                qc.cx(q, q + 1)
    return qc


def first_gradient(qc, obs, theta):
    shift = np.zeros_like(theta)
    shift[0] = np.pi / 2
    evs = estimator.run([(qc, obs, np.array([theta + shift, theta - shift]))]).result()[0].data.evs
    return 0.5 * (evs[0] - evs[1])


def gradient_variance(n, n_samples=100):
    qc = wide_ansatz(n, reps=n)
    obs = SparsePauliOp("I" * (n - 2) + "ZZ")
    return float(
        np.var([first_gradient(qc, obs, rng.uniform(0, 2 * np.pi, qc.num_parameters)) for _ in range(n_samples)])
    )


variances = {n: gradient_variance(n) for n in (2, 3, 5, 6, 8)}
variances[4] = gradient_variance(4)
ns = sorted(variances)
v = np.array([variances[n] for n in ns])
slope, intercept = np.polyfit(ns, np.log(v), 1)
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.semilogy(ns, v, "o", color=BLUE, label="measured, 100 random parameter sets")
ax.semilogy(
    ns, np.exp(intercept + slope * np.array(ns)), "--", color=GRAY, label=rf"fit $\propto {np.exp(slope):.2f}^{{\,n}}$"
)
ax.set_xlabel("qubits $n$ (and entangling layers)")
ax.set_ylabel(r"$\mathrm{Var}\,[\partial_{\theta_1}\langle Z_0Z_1\rangle]$")
ax.legend(frameon=False)
fig.savefig(OUT / "barren_plateau.pdf")
plt.close(fig)
print(
    "[5/6] barren_plateau.pdf   variances:",
    {n: f"{variances[n]:.2e}" for n in ns},
    f"; fit factor per qubit {np.exp(slope):.3f}, ratio var(2)/var(8) = {variances[2] / variances[8]:.0f}",
)

# Numbers for the hardware section
x_a, x_b = X_circ[0], X_circ[1]
print(f"[6/6] simulator kernel entry k(x_0, x_1) = {kernel_matrix(x_a[None, :], x_b[None, :])[0, 0]:.4f}")
