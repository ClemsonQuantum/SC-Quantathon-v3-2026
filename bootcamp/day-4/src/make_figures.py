"""Figures and numbers for the Day 4 notes. Run from this folder in the scqv3 env: python make_figures.py

Draws the figures from the counts the executed solutions notebook printed (September 15, 2026), copied in as data,
so the notes quote what the notebook shows; the R_y sweep is a seeded reproduction, since the notebook only plots it.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import Pauli, SparsePauliOp, Statevector, hellinger_fidelity, partial_trace

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
SHOTS = 1000
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
BLUE, ORANGE, GREEN, GRAY = "#1f77b4", "#ff7f0e", "#2ca02c", "0.45"


def counts_of(qc):
    return sampler.run([qc], shots=SHOTS).result()[0].data.meas.get_counts()


# Counts printed by the executed solutions notebook
NB_BASES = {"Z": {"0": 470, "1": 530}, "X": {"0": 503, "1": 497}, "Y": {"0": 1000}}
NB_PREDICT = {"z": 0.243, "x": 0.935}
NB_RY = {"0": 222, "1": 778}
NB_BELL = {"00": 504, "11": 496}
NB_QPU = {
    "00": 512,
    "11": 478,
    "01": 6,
    "10": 4,
}  # ibm_kingston (Heron r2), physical qubits 55 and 59, job dal16o6lg97s73c8dh90
NB_CORR = {
    ("Bell state", "Z"): {"00": 493, "11": 507},
    ("Bell state", "X"): {"00": 493, "11": 507},
    (r"$|+\rangle|+\rangle$", "Z"): {"00": 226, "01": 264, "10": 257, "11": 253},
    (r"$|+\rangle|+\rangle$", "X"): {"00": 1000},
}
NB_YY = {"01": 516, "10": 484}
NB_GHZ = {"00000": 508, "11111": 492}


def expectation(qc, label):
    return float(estimator.run([(qc, SparsePauliOp(label))]).result()[0].data.evs)


def bloch(state):
    return np.array([state.expectation_value(Pauli(a)).real for a in "XYZ"])


def bars(ax, counts, color, label=None, offset=0.0, width=0.55):
    keys = ["00", "01", "10", "11"]
    b = ax.bar(np.arange(4) + offset, [counts.get(k, 0) for k in keys], width, color=color, label=label)
    ax.bar_label(b, padding=2, fontsize=8)
    ax.set_xticks(np.arange(4), keys)


# Figure 1: two rotation paths on the Bloch sphere: R_y(theta)|0> along a meridian, P(lambda)|+> along the equator
fig = plt.figure(figsize=(5.2, 5.2))
ax = fig.add_subplot(111, projection="3d")
u, v = np.mgrid[0 : 2 * np.pi : 13j, 0 : np.pi : 7j]
ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="0.88", lw=0.5)
for label, (x, y, z, dx, dy, dz) in {
    r"$|0\rangle$": (0, 0, 1, 0, 0, 0.14),
    r"$|1\rangle$": (0, 0, -1, 0, 0, -0.16),
    r"$|+\rangle$": (1, 0, 0, 0.22, 0, -0.06),
    r"$|-\rangle$": (-1, 0, 0, -0.22, 0, 0.04),
    r"$|{+}i\rangle$": (0, 1, 0, 0.1, 0.3, -0.14),
}.items():
    ax.plot([0, x], [0, y], [0, z], color=GRAY, lw=0.8)
    ax.scatter([x], [y], [z], color="k", s=12, depthshade=False)
    ax.text(x + dx, y + dy, z + dz, label, ha="center", va="center", fontsize=11)
th = np.linspace(0, np.pi, 60)
ry_path = np.array([bloch(Statevector([np.cos(t / 2), np.sin(t / 2)])) for t in th])
ax.plot(ry_path[:, 0], ry_path[:, 1], ry_path[:, 2], color=BLUE, lw=2.2, label=r"$R_y(\theta)|0\rangle$")
lam = np.linspace(0, 2 * np.pi, 120)
p_path = np.array([bloch(Statevector([1, np.exp(1j * lam_k)]) / np.sqrt(2)) for lam_k in lam])
ax.plot(p_path[:, 0], p_path[:, 1], p_path[:, 2], color=ORANGE, lw=2.2, label=r"$P(\lambda)|+\rangle$")
ax.set_xlim(-0.95, 0.95)
ax.set_ylim(-0.95, 0.95)
ax.set_zlim(-0.95, 0.95)
ax.set_box_aspect((1, 1, 1))
ax.set_axis_off()
ax.view_init(elev=22, azim=-55)
ax.legend(frameon=False, loc="lower center", ncol=2)
fig.savefig(OUT / "rotation_paths.pdf")
plt.close(fig)
print("[1/7] rotation_paths.pdf")

# Figure 2: R_y sweep, exact and sampled
thetas = np.linspace(0, 2 * np.pi, 25)
p1_exact, p1_sampled = [], []
for t in thetas:
    qc = QuantumCircuit(1)
    qc.ry(t, 0)
    p1_exact.append(Statevector(qc).probabilities()[1])
    qc.measure_all()
    p1_sampled.append(counts_of(qc).get("1", 0) / SHOTS)
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.plot(thetas, np.sin(thetas / 2) ** 2, "-", color=GRAY, label=r"$\sin^2(\theta/2)$")
ax.plot(thetas, p1_exact, "s", ms=4, color=BLUE, label="Statevector")
ax.plot(thetas, p1_sampled, "o", ms=4, color=ORANGE, label=f"{SHOTS} shots")
ax.set_xlabel(r"$\theta$")
ax.set_ylabel("$P(1)$")
ax.legend(frameon=False)
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi], ["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"])
fig.savefig(OUT / "ry_sweep.pdf")
plt.close(fig)
print("[2/7] ry_sweep.pdf   max |sampled - exact| =", round(float(np.max(np.abs(np.array(p1_sampled) - p1_exact))), 3))


# Figure 3: |+i> read in three bases (the notebook's own counts)
basis_counts = NB_BASES
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax, (b, c), color in zip(axes, basis_counts.items(), [BLUE, ORANGE, GREEN]):
    bb = ax.bar(["0", "1"], [c.get("0", 0), c.get("1", 0)], color=color, width=0.55)
    ax.bar_label(bb, padding=2, fontsize=8)
    ax.set_title(f"${b}$ basis")
    ax.set_xlabel("outcome")
    ax.set_ylim(0, 1150)
axes[0].set_ylabel(f"counts out of {SHOTS}")
fig.savefig(OUT / "three_bases.pdf")
plt.close(fig)
print("[3/7] three_bases.pdf   counts:", basis_counts)

# Numbers for the predict-then-measure exercise
prep_t = QuantumCircuit(1)
prep_t.ry(2 * np.pi / 3, 0)
sv = Statevector(prep_t)
exact_z = sv.probabilities()[0]
exact_x = abs(Statevector.from_label("+").inner(sv)) ** 2
print(
    "      predict-then-measure: exact P(0)_Z =",
    round(float(exact_z), 4),
    " measured",
    NB_PREDICT["z"],
    " | exact P(+) =",
    round(float(exact_x), 4),
    " measured",
    NB_PREDICT["x"],
    " | R_y(2pi/3) single run:",
    NB_RY,
)

# Figure 4: the Bell circuit
bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell_meas = bell.copy()
bell_meas.measure_all()
fig = bell_meas.draw("mpl", style="clifford")
fig.savefig(OUT / "bell_circuit.pdf")
plt.close(fig)
print("[4/7] bell_circuit.pdf")

bell_counts = NB_BELL
print("      Bell counts, 1000 shots:", bell_counts)


# Figure 5: correlations in two bases, Bell vs |+>|+>
def measure_both(prep, basis):
    qc = prep.copy()
    if basis == "X":
        qc.h(0)
        qc.h(1)
    qc.measure_all()
    return counts_of(qc)


plus_plus = QuantumCircuit(2)
plus_plus.h(0)
plus_plus.h(1)
fig, axes = plt.subplots(2, 2, figsize=(6.8, 4.6), sharey=True)
res = {}
for i, (name, _prep) in enumerate([("Bell state", bell), (r"$|+\rangle|+\rangle$", plus_plus)]):
    for j, basis in enumerate("ZX"):
        c = NB_CORR[(name, basis)]
        res[(name, basis)] = c
        bars(axes[i, j], c, BLUE if i == 0 else ORANGE)
        axes[i, j].set_title(f"{name}, ${basis}{basis}$ basis")
        axes[i, j].set_ylim(0, 1150)
for ax in axes[1]:
    ax.set_xlabel("outcome")
for ax in axes[:, 0]:
    ax.set_ylabel("counts")
fig.tight_layout()
fig.savefig(OUT / "correlations.pdf")
plt.close(fig)
print("[5/7] correlations.pdf   ", {f"{k[0]} {k[1]}{k[1]}": v for k, v in res.items()})
print(
    "      <ZZ>,<XX>,<YY>,<ZX> Bell:",
    [round(expectation(bell, p), 3) for p in ("ZZ", "XX", "YY", "ZX")],
    " |+>|+>:",
    [round(expectation(plus_plus, p), 3) for p in ("ZZ", "XX", "YY", "ZX")],
)
print("      Bell in the YY basis:", NB_YY)


# GHZ and W numbers
def ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    return qc


print("      GHZ(5) counts:", NB_GHZ)
print("      purity after losing one qubit of GHZ(3):", round(partial_trace(Statevector(ghz(3)), [2]).purity().real, 3))

# Figure 6: memory of a state vector against qubit count
n_axis = np.arange(1, 51)
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.semilogy(n_axis, 2.0**n_axis * 16, color=BLUE, label="state vector, bytes")
ax.axhline(16 * 2**30, ls="--", lw=0.8, color=GRAY)
ax.text(1.5, 16 * 2**30 * 2.2, "16 GB laptop", fontsize=8, color=GRAY)
ax.axhline(2**60, ls="--", lw=0.8, color=GRAY)
ax.text(1.5, 2**60 * 2.2, "1 EiB (56 qubits)", fontsize=8, color=GRAY)
ax.set_xlabel("qubits $n$")
ax.set_ylabel("memory (bytes)")
ax.legend(frameon=False, loc="lower right")
fig.savefig(OUT / "memory_scaling.pdf")
plt.close(fig)
print("[6/7] memory_scaling.pdf")

# Figure 7: the Bell state three ways (section 13)
exact = {"00": 500, "11": 500}
fig, ax = plt.subplots(figsize=(5.2, 3.0))
bars(ax, exact, GRAY, "exact (Born rule)", -0.26, 0.26)
bars(ax, NB_BELL, BLUE, "simulator", 0.0, 0.26)
bars(ax, NB_QPU, ORANGE, "ibm_kingston", 0.26, 0.26)
ax.set_xlabel("outcome")
ax.set_ylabel(f"counts out of {SHOTS}")
ax.set_ylim(0, 640)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=3)
fig.savefig(OUT / "bell_hardware.pdf")
plt.close(fig)
imp = (NB_QPU.get("01", 0) + NB_QPU.get("10", 0)) / SHOTS
print(
    "[7/7] bell_hardware.pdf   hardware:",
    NB_QPU,
    f" impossible {imp:.1%}, Hellinger fidelity to the exact distribution {hellinger_fidelity(exact, NB_QPU):.3f}, to the simulator run {hellinger_fidelity(NB_BELL, NB_QPU):.3f}",
)
