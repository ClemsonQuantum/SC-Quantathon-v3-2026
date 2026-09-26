"""Figures and numbers for the Day 6 notes. Run from this folder in the scqv3 env: python make_figures.py

Reproduces the notebook's experiments with the notebook's seeds, saves vector figures to figures/, and prints
the numbers quoted in notes.tex. The H2 coefficient table is O'Malley et al., Phys. Rev. X 6, 031007 (2016), Table I.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from scipy.optimize import minimize, minimize_scalar

warnings.filterwarnings("ignore")
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
SHOTS = 1000
NOISY_SHOTS = 10_000
rng = np.random.default_rng(seed=3)
sampler = StatevectorSampler(seed=np.random.default_rng(7))
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
BLUE, ORANGE, GREEN, RED, GRAY = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "0.45"


# Figure 1: the hardware-efficient ansatz
def hardware_efficient(n, reps):
    params = ParameterVector("theta", n * (reps + 1))
    qc = QuantumCircuit(n)
    k = 0
    for layer in range(reps + 1):
        for q in range(n):
            qc.ry(params[k], q)
            k += 1
        if layer < reps:
            for q in range(n - 1):
                qc.cx(q, q + 1)
            qc.barrier()
    return qc


ansatz = hardware_efficient(2, 1)
fig = ansatz.draw("mpl", style="clifford")
fig.savefig(OUT / "ansatz.pdf")
plt.close(fig)
print("[1/7] ansatz.pdf   parameters:", ansatz.num_parameters)

H = SparsePauliOp.from_list(
    [
        ("II", -1.052373245772859),
        ("IZ", 0.39793742484318045),
        ("ZI", -0.39793742484318045),
        ("ZZ", -0.01128010425623538),
        ("XX", 0.18093119978423156),
    ]
)
eig = np.linalg.eigvalsh(H.to_matrix())
E0 = eig.min()
print("      eigenvalues:", np.round(eig, 4), " E0 =", round(float(E0), 6))


def energy(p):
    return float(estimator.run([(ansatz, H, p)]).result()[0].data.evs)


# Figure 2: one-parameter landscape
def one(t):
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.ry(t, 1)
    qc.cx(1, 0)
    return qc


ts = np.linspace(-np.pi, np.pi, 121)
land = [float(estimator.run([(one(t), H)]).result()[0].data.evs) for t in ts]
tb = ts[int(np.argmin(land))]
fig, ax = plt.subplots(figsize=(4.6, 2.8))
ax.plot(ts, land, color=BLUE)
ax.axhline(E0, color=GRAY, ls="--", label="exact $E_0$")
ax.plot(tb, min(land), "o", color=ORANGE, label=rf"minimum, $\theta = {tb:.3f}$")
ax.set_xlabel(r"$\theta$")
ax.set_ylabel("energy (hartree)")
ax.legend(frameon=False)
fig.savefig(OUT / "landscape.pdf")
plt.close(fig)
print(f"[2/7] landscape.pdf   min {min(land):.6f} at theta {tb:.4f}")

# Figure 3: VQE convergence (same seed sequence as the notebook)
rng.uniform(0, 2 * np.pi, 4)  # random_angles
test_params = rng.uniform(0, 2 * np.pi, 4)  # test_params
for _ in range(20):
    rng.uniform(0, 2 * np.pi, 4)  # the twenty variational-principle checks
trace = []


def traced(p):
    trace.append(energy(p))
    return trace[-1]


x0 = rng.uniform(0, 2 * np.pi, 4)
res = minimize(traced, x0, method="COBYLA", options={"maxiter": 200})
fig, ax = plt.subplots(figsize=(4.6, 2.8))
ax.plot(trace, ".-", color=BLUE, ms=4, lw=0.8)
ax.axhline(E0, color=GRAY, ls="--", label="exact $E_0$")
ax.set_xlabel("energy evaluation")
ax.set_ylabel("energy (hartree)")
ax.legend(frameon=False)
fig.savefig(OUT / "vqe_convergence.pdf")
plt.close(fig)
print(f"[3/7] vqe_convergence.pdf   final {res.fun:.6f}, error {res.fun - E0:.2e}, evaluations {len(trace)}")


# Section 5: parameter shift and the three optimizers
def ps_grad(p):
    g = np.zeros(len(p))
    for k in range(len(p)):
        s = np.zeros(len(p))
        s[k] = np.pi / 2
        g[k] = 0.5 * (energy(p + s) - energy(p - s))
    return g


def fd_grad(p, h=1e-4):
    g = np.zeros(len(p))
    for k in range(len(p)):
        s = np.zeros(len(p))
        s[k] = h
        g[k] = (energy(p + s) - energy(p - s)) / (2 * h)
    return g


print(
    "      gradient at test_params: shift",
    np.round(ps_grad(test_params), 4),
    " max |shift - fd| =",
    f"{np.abs(ps_grad(test_params) - fd_grad(test_params)).max():.1e}",
)
evaluations = [0]


def counted(p):
    evaluations[0] += 1
    return energy(p)


def gradient_descent(f, x0, lr=1.0, steps=100):
    x = np.array(x0, float)
    hist = [f(x)]
    for _ in range(steps):
        g = np.zeros(len(x))
        for k in range(len(x)):
            s = np.zeros(len(x))
            s[k] = np.pi / 2
            g[k] = 0.5 * (f(x + s) - f(x - s))
        x = x - lr * g
        hist.append(f(x))
    return x, hist


def spsa(f, x0, steps=200, a=2.0, c=0.2, A=10, seed=11):
    r = np.random.default_rng(seed)
    x = np.array(x0, float)
    hist = [f(x)]
    for k in range(steps):
        a_k, c_k = a / (k + 1 + A) ** 0.602, c / (k + 1) ** 0.101
        d = r.choice([-1, 1], size=len(x))
        g = (f(x + c_k * d) - f(x - c_k * d)) / (2 * c_k) * d
        x = x - a_k * g
        hist.append(f(x))
    return x, hist


runs = {}
evaluations[0] = 0
_, h = gradient_descent(counted, x0)
runs["gradient descent"] = (h, evaluations[0])
evaluations[0] = 0
_, h = spsa(counted, x0)
runs["SPSA"] = (h, evaluations[0])
evaluations[0] = 0
ct = []
minimize(lambda p: ct.append(counted(p)) or ct[-1], x0, method="COBYLA", options={"maxiter": 200})
runs["COBYLA"] = (ct, evaluations[0])
fig, ax = plt.subplots(1, 2, figsize=(8, 2.9))
for (name, (h, _n_ev)), col in zip(runs.items(), [BLUE, ORANGE, GREEN]):
    ax[0].plot(h, color=col, label=name, lw=1)
    ax[1].semilogy(np.maximum(np.array(h) - E0, 1e-12), color=col, label=name, lw=1)
ax[0].axhline(E0, color=GRAY, ls="--")
ax[0].set_ylabel("energy (hartree)")
ax[1].set_ylabel("energy $- E_0$ (hartree)")
for a_ in ax:
    a_.set_xlabel("optimizer step")
    a_.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "optimizers.pdf")
plt.close(fig)
print("[4/7] optimizers.pdf")
for name, (h, n_ev) in runs.items():
    print(f"      {name:<17} final {h[-1]:.6f}  error {h[-1] - E0:.1e}  steps {len(h) - 1}  evaluations {n_ev}")

# Section 6: the energy under noise
theta_opt = res.x
bound = ansatz.assign_parameters(theta_opt)
E_exact = energy(theta_opt)
labels = ["00", "01", "10", "11"]
coef = {label: c.real for label, c in H.to_list()}


def z_circuit(qc):
    c = qc.copy()
    c.measure_all()
    return c


def x_circuit(qc):
    c = qc.copy()
    c.h([0, 1])
    c.measure_all()
    return c


def probs_of(counts):
    n = sum(counts.values())
    return {k: counts.get(k, 0) / n for k in labels}


def z_terms(p):
    z0 = sum(v * (1 if k[1] == "0" else -1) for k, v in p.items())
    z1 = sum(v * (1 if k[0] == "0" else -1) for k, v in p.items())
    zz = sum(v * (1 if k[0] == k[1] else -1) for k, v in p.items())
    return z0, z1, zz


def energy_from_probs(pz, px):
    z0, z1, zz = z_terms(pz)
    xx = z_terms(px)[2]
    return coef["II"] + coef["IZ"] * z0 + coef["ZI"] * z1 + coef["ZZ"] * zz + coef["XX"] * xx


def counts_of(qc, shots=SHOTS):
    return sampler.run([qc], shots=shots).result()[0].data.meas.get_counts()


E_shots = energy_from_probs(probs_of(counts_of(z_circuit(bound))), probs_of(counts_of(x_circuit(bound))))
backend = FakeSherbrooke()
noisy_backend = AerSimulator.from_backend(backend)
noise_rng = np.random.default_rng(5)


def next_seed():
    return int(noise_rng.integers(2**31 - 1))


physical = (
    generate_preset_pass_manager(optimization_level=3, backend=backend, seed_transpiler=1)
    .run(z_circuit(bound))
    .layout.final_index_layout()
)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=physical)


def run_noisy(qc, shots=NOISY_SHOTS):
    return noisy_backend.run(pm.run(qc), shots=shots, seed_simulator=next_seed()).result().get_counts()


isa_z = pm.run(z_circuit(bound))
z_counts = run_noisy(z_circuit(bound))
x_counts = run_noisy(x_circuit(bound))
E_noisy = energy_from_probs(probs_of(z_counts), probs_of(x_counts))
M = np.zeros((4, 4))
for j, label in enumerate(labels):
    qc = QuantumCircuit(2)
    for q, bit in enumerate(reversed(label)):
        if bit == "1":
            qc.x(q)
    qc.measure_all()
    c = run_noisy(qc)
    for i, out in enumerate(labels):
        M[i, j] = c.get(out, 0) / NOISY_SHOTS


def mitigate(counts):
    p = np.array([counts.get(k, 0) for k in labels], float)
    p /= p.sum()
    t = np.clip(np.linalg.solve(M, p), 0, None)
    t /= t.sum()
    return dict(zip(labels, t))


E_mit = energy_from_probs(mitigate(z_counts), mitigate(x_counts))
LIVE_ENERGY, LIVE_STD = (
    -1.8471,
    0.0041,
)  # ibm_marrakesh (Heron r2), qubits 14 and 15, ISA depth 11 with one cz, runtime Estimator resilience_level 1, 4096 shots, job dam7batr85ps73fcbtb0
rows = [
    ("exact", E_exact),
    (f"{SHOTS} shots per basis", E_shots),
    ("noisy simulator", E_noisy),
    ("noisy, readout mitigated", E_mit),
    ("ibm_marrakesh, TREX", LIVE_ENERGY),
]
print(
    f"[5/7] noisy_vqe.pdf   physical qubits {physical}, ISA depth {isa_z.depth()}, ops {dict(isa_z.count_ops())}, M diag {np.round(np.diag(M), 3)}"
)
for name, e in rows:
    print(f"      {name:<26} {e:.4f}  error {e - E_exact:+.4f}")
print(f"      noisy Z-basis counts {z_counts}   X-basis counts {x_counts}")
fig, ax = plt.subplots(figsize=(6.2, 2.7))
errs = [1e3 * (e - E_exact) for _, e in rows[1:]]
b = ax.bar(
    [r[0].replace(", ", ",\n") for r in rows[1:]],
    errs,
    color=[BLUE, RED, GREEN, ORANGE],
    width=0.55,
    yerr=[0, 0, 0, 1e3 * LIVE_STD],
    capsize=3,
)
ax.bar_label(b, labels=[f"{e:+.1f}" for e in errs], padding=2, fontsize=8)
ax.axhline(0, color=GRAY, lw=0.8)
ax.set_ylabel("energy error (millihartree)")
ax.set_title("energy at the optimal angles, error against exact")
fig.savefig(OUT / "noisy_vqe.pdf")
plt.close(fig)

# Section 7: ansatz comparison and the dissociation curve
evaluations[0] = 0
r_he = minimize(counted, x0, method="COBYLA", options={"maxiter": 300})
n_he = evaluations[0]
evaluations[0] = 0


def e1(p):
    evaluations[0] += 1
    return float(estimator.run([(one(p[0]), H)]).result()[0].data.evs)


r_one = minimize(e1, [x0[0]], method="COBYLA", options={"maxiter": 300})
n_one = evaluations[0]
print(
    f"[6/7] ansatz comparison: hardware efficient error {r_he.fun - E0:.1e} after {n_he} evaluations; one parameter error {r_one.fun - E0:.1e} after {n_one}"
)
h2_table = np.array(
    [
        [0.30, 1.7252, 0.5215, -1.1458, 0.6631, 0.0806],
        [0.35, 1.3827, 0.4982, -1.0226, 0.6537, 0.0815],
        [0.40, 1.1182, 0.4754, -0.9145, 0.6438, 0.0825],
        [0.45, 0.9083, 0.4534, -0.8194, 0.6336, 0.0835],
        [0.50, 0.7381, 0.4325, -0.7355, 0.6233, 0.0846],
        [0.55, 0.5979, 0.4125, -0.6612, 0.6129, 0.0858],
        [0.60, 0.4808, 0.3937, -0.5950, 0.6025, 0.0870],
        [0.65, 0.3819, 0.3760, -0.5358, 0.5921, 0.0883],
        [0.70, 0.2976, 0.3593, -0.4826, 0.5818, 0.0896],
        [0.75, 0.2252, 0.3435, -0.4347, 0.5716, 0.0910],
        [0.80, 0.1626, 0.3288, -0.3915, 0.5616, 0.0925],
        [0.85, 0.1083, 0.3149, -0.3523, 0.5518, 0.0939],
        [0.90, 0.0609, 0.3018, -0.3168, 0.5421, 0.0954],
        [0.95, 0.0193, 0.2895, -0.2845, 0.5327, 0.0970],
        [1.00, -0.0172, 0.2779, -0.2550, 0.5235, 0.0986],
        [1.05, -0.0493, 0.2669, -0.2282, 0.5146, 0.1002],
        [1.10, -0.0778, 0.2565, -0.2036, 0.5059, 0.1018],
        [1.15, -0.1029, 0.2467, -0.1810, 0.4974, 0.1034],
        [1.20, -0.1253, 0.2374, -0.1603, 0.4892, 0.1050],
        [1.25, -0.1452, 0.2286, -0.1413, 0.4812, 0.1067],
        [1.30, -0.1629, 0.2203, -0.1238, 0.4735, 0.1083],
        [1.35, -0.1786, 0.2123, -0.1077, 0.4660, 0.1100],
        [1.40, -0.1927, 0.2048, -0.0929, 0.4588, 0.1116],
        [1.45, -0.2053, 0.1976, -0.0792, 0.4518, 0.1133],
        [1.50, -0.2165, 0.1908, -0.0666, 0.4451, 0.1149],
        [1.55, -0.2265, 0.1843, -0.0549, 0.4386, 0.1165],
        [1.60, -0.2355, 0.1782, -0.0442, 0.4323, 0.1181],
        [1.65, -0.2436, 0.1723, -0.0342, 0.4262, 0.1196],
        [1.70, -0.2508, 0.1667, -0.0251, 0.4204, 0.1211],
        [1.75, -0.2573, 0.1615, -0.0166, 0.4148, 0.1226],
        [1.80, -0.2632, 0.1565, -0.0088, 0.4094, 0.1241],
        [1.85, -0.2684, 0.1517, -0.0015, 0.4042, 0.1256],
        [1.90, -0.2731, 0.1472, 0.0052, 0.3992, 0.1270],
        [1.95, -0.2774, 0.1430, 0.0114, 0.3944, 0.1284],
        [2.00, -0.2812, 0.1390, 0.0171, 0.3898, 0.1297],
        [2.05, -0.2847, 0.1352, 0.0223, 0.3853, 0.1310],
        [2.10, -0.2879, 0.1316, 0.0272, 0.3811, 0.1323],
        [2.15, -0.2908, 0.1282, 0.0317, 0.3769, 0.1335],
        [2.20, -0.2934, 0.1251, 0.0359, 0.3730, 0.1347],
        [2.25, -0.2958, 0.1221, 0.0397, 0.3692, 0.1359],
        [2.30, -0.2980, 0.1193, 0.0432, 0.3655, 0.1370],
        [2.35, -0.3000, 0.1167, 0.0465, 0.3620, 0.1381],
        [2.40, -0.3018, 0.1142, 0.0495, 0.3586, 0.1392],
        [2.45, -0.3035, 0.1119, 0.0523, 0.3553, 0.1402],
        [2.50, -0.3051, 0.1098, 0.0549, 0.3521, 0.1412],
    ]
)
Rs = h2_table[:, 0]


def h2(row):
    g0, g1, g2, g3, g4 = row[1:]
    return SparsePauliOp.from_list([("II", g0), ("IZ", g1), ("ZI", g2), ("ZZ", g3), ("XX", g4), ("YY", g4)])


exact = np.array([np.linalg.eigvalsh(h2(r).to_matrix()).min() for r in h2_table])
hf = np.array([Statevector.from_label("01").expectation_value(h2(r)).real for r in h2_table])
vqe = np.array(
    [
        minimize_scalar(
            lambda t, Hr=h2(r): float(estimator.run([(one(t), Hr)]).result()[0].data.evs),
            bounds=(-np.pi, np.pi),
            method="bounded",
        ).fun
        for r in h2_table
    ]
)
i = int(np.argmin(vqe))
De = vqe[-1] - vqe[i]
fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.plot(Rs, exact, "-", color=GRAY, label="exact eigenvalue")
ax.plot(Rs, hf, ":", color=ORANGE, label=r"Hartree-Fock state $\ket{01}$".replace(r"\ket{01}", "|01\\rangle"))
ax.plot(Rs, vqe, "o", ms=3.5, color=BLUE, label="VQE, one-parameter ansatz")
ax.set_xlabel(r"bond length $R$ (\AA)".replace(r"\AA", "Å"))
ax.set_ylabel("energy (hartree)")
ax.legend(frameon=False)
fig.savefig(OUT / "dissociation.pdf")
plt.close(fig)
j = int(np.where(np.isclose(Rs, 0.75))[0][0])
print(
    f"[7/7] dissociation.pdf   max |VQE - exact| {np.abs(vqe - exact).max():.1e}; minimum {vqe[i]:.4f} at R = {Rs[i]:.2f}; "
    f"HF at 0.75 {hf[j]:.4f} (gap {hf[j] - exact[j]:.4f}); at 2.50 exact {exact[-1]:.4f}, HF {hf[-1]:.4f} (gap {hf[-1] - exact[-1]:.4f}); "
    f"E(2.5) - E(min) = {De:.4f} hartree = {De * 27.2114:.2f} eV"
)

# Figure 8 (section 8): MaxCut on the square and the QAOA samples (rng continues from x0, as in the notebook)
n = 4
edges = [(0, 1), (1, 2), (2, 3), (3, 0)]


def cut(bs):
    b = bs[::-1]
    return sum(1 for i, j in edges if b[i] != b[j])


C = SparsePauliOp.from_sparse_list([("ZZ", [i, j], -0.5) for i, j in edges], num_qubits=n) + SparsePauliOp(
    "I" * n, 0.5 * len(edges)
)


def qaoa(p):
    g = ParameterVector("gamma", p)
    b = ParameterVector("beta", p)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(p):
        for i, j in edges:
            qc.rzz(2 * g[layer], i, j)
        qc.rx(2 * b[layer], range(n))
        qc.barrier()
    return qc


qc2 = qaoa(2)


def negcut(p):
    return -float(estimator.run([(qc2, C, p)]).result()[0].data.evs)


best = None
restarts = []
for _ in range(3):
    x = rng.uniform(0, np.pi, 4)
    s = minimize(negcut, x, method="COBYLA", options={"maxiter": 300})
    restarts.append(-s.fun)
    if best is None or s.fun < best.fun:
        best = s
qs = qc2.assign_parameters(best.x)
qs.measure_all()
counts = counts_of(qs)
fig, axes = plt.subplots(1, 2, figsize=(8, 2.9), gridspec_kw={"width_ratios": [1, 1.6]})
pos = {0: (0, 1), 1: (1, 1), 2: (1, 0), 3: (0, 0)}
top = max(counts, key=counts.get)
color_of = {i: (ORANGE if top[::-1][i] == "1" else BLUE) for i in range(n)}
for i, j in edges:
    axes[0].plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]], color=GRAY, lw=1.5, zorder=1)
for i, (px, py) in pos.items():
    axes[0].scatter([px], [py], s=500, color=color_of[i], zorder=2)
    axes[0].text(px, py, str(i), ha="center", va="center", color="white", fontsize=11)
axes[0].set_xlim(-0.5, 1.5)
axes[0].set_ylim(-0.5, 1.5)
axes[0].set_axis_off()
axes[0].set_title(f"coloring {top}: cut {cut(top)} of {len(edges)}")
keys = sorted(counts)
vals = [counts[k] for k in keys]
bars = axes[1].bar(keys, vals, color=[ORANGE if cut(k) == 4 else GRAY for k in keys])
axes[1].bar_label(bars, padding=2, fontsize=8)
axes[1].set_ylabel("counts")
axes[1].set_title("samples of the optimized QAOA state, $p = 2$")
axes[1].set_ylim(0, 620)
fig.tight_layout()
fig.savefig(OUT / "maxcut_qaoa.pdf")
plt.close(fig)
good = sum(v for k, v in counts.items() if cut(k) == 4) / SHOTS
print(
    f"[8/8] maxcut_qaoa.pdf   restarts <C>: {np.round(restarts, 4)}; best {-best.fun:.4f}; samples {counts}; max-cut fraction {good:.0%}"
)
