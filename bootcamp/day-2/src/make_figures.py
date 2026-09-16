"""Figures and numbers for the Day 2 notes. Run from this folder in the scqv3 env: python make_figures.py

Reproduces the notebook's experiments with fixed seeds, saves vector figures to figures/, and prints the numbers
quoted in notes.tex. Counts that the executed solutions notebook printed (September 15, 2026) are copied in as data,
including the recorded ibm_kingston run of section 9.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Pauli
from qiskit.visualization import plot_bloch_multivector
from qiskit_aer import AerSimulator

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
SEED = 7
SHOTS = 1000
DIRECT_COUNTS = [{"0": 502, "1": 498}, {"0": 511, "1": 489}]                  # notebook section 5, |+> and |-> measured directly
SIM_FOUR = [{"0": 487, "1": 513}, {"0": 505, "1": 495}, {"0": 1000}, {"1": 1000}]   # notebook section 9, simulator
QPU_FOUR = [{"0": 308, "1": 692}, {"0": 299, "1": 701}, {"0": 453, "1": 547}, {"0": 148, "1": 852}]   # ibm_kingston, qubit 0, job dal14kot9ckc739kv7n0
LABELS = ["|+> direct", "|-> direct", "|+> after H", "|-> after H"]

plt.rcParams.update({
    "font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, ORANGE, GRAY = "#1f77b4", "#ff7f0e", "0.45"
rng = np.random.default_rng(SEED)
def seed():
    return int(rng.integers(2 ** 31 - 1))
sim = AerSimulator()
def run(qc): return sim.run(qc, shots=SHOTS, seed_simulator=seed()).result().get_counts()

# Figure 1: a complex number in polar form on the unit circle
fig, ax = plt.subplots(figsize=(3.4, 3.4))
t = np.linspace(0, 2 * np.pi, 400)
ax.plot(np.cos(t), np.sin(t), color=GRAY, lw=0.8)
ax.axhline(0, color=GRAY, lw=0.5); ax.axvline(0, color=GRAY, lw=0.5)
phi = np.radians(40)
ax.annotate("", xy=(np.cos(phi), np.sin(phi)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.6))
arc = np.linspace(0, phi, 50)
ax.plot(0.3 * np.cos(arc), 0.3 * np.sin(arc), color=BLUE, lw=1)
ax.text(0.36, 0.09, r"$\phi$", color=BLUE)
ax.text(np.cos(phi) + 0.05, np.sin(phi) + 0.03, r"$e^{i\phi} = \cos\phi + i\sin\phi$")
ax.plot([np.cos(phi), np.cos(phi)], [0, np.sin(phi)], ls=":", color=BLUE, lw=0.8)
ax.plot([0, np.cos(phi)], [np.sin(phi), np.sin(phi)], ls=":", color=BLUE, lw=0.8)
ax.text(np.cos(phi) - 0.02, -0.14, r"$\cos\phi$", ha="center", fontsize=9)
ax.text(-0.3, np.sin(phi) - 0.03, r"$\sin\phi$", fontsize=9)
ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_aspect("equal")
ax.set_xlabel("real part"); ax.set_ylabel("imaginary part")
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
fig.savefig(OUT / "unit_circle.pdf"); plt.close(fig)
print("[1/7] unit_circle.pdf")

# Figure 2: |+> sampled
sv_plus = Statevector.from_label("+")
sv_plus.seed(rng)
plus_counts = sv_plus.sample_counts(SHOTS)
fig, ax = plt.subplots(figsize=(3.6, 2.8))
bars = ax.bar(["0", "1"], [plus_counts.get("0", 0), plus_counts.get("1", 0)], color=BLUE, width=0.55)
ax.bar_label(bars, padding=2, fontsize=9)
ax.axhline(SHOTS / 2, ls="--", lw=0.8, color=GRAY)
ax.set_xlabel("outcome"); ax.set_ylabel(f"counts out of {SHOTS}"); ax.set_ylim(0, 620)
fig.savefig(OUT / "plus_sampled.pdf"); plt.close(fig)
print("[2/7] plus_sampled.pdf   counts:", dict(plus_counts))

# Figure 3: |+> and |-> measured directly, and after H
def prep(sign):
    qc = QuantumCircuit(1); qc.h(0)
    if sign < 0: qc.z(0)
    return qc
panels = []
for with_h in (False, True):
    row = []
    for sign in (+1, -1):
        qc = prep(sign)
        if with_h: qc.h(0)
        qc.measure_all(); row.append(run(qc))
    panels.append(row)
panels[0] = DIRECT_COUNTS                       # the notebook's seeded StatevectorSampler numbers
fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.8), sharey=True)
for ax, row, title in zip(axes, panels, ["measured directly", r"$H$, then measured"]):
    x = np.arange(2); w = 0.36
    b1 = ax.bar(x - w / 2, [row[0].get(k, 0) for k in "01"], w, label=r"$|+\rangle$", color=BLUE)
    b2 = ax.bar(x + w / 2, [row[1].get(k, 0) for k in "01"], w, label=r"$|-\rangle$", color=ORANGE)
    ax.bar_label(b1, padding=2, fontsize=8); ax.bar_label(b2, padding=2, fontsize=8)
    ax.set_xticks(x, ["0", "1"]); ax.set_xlabel("outcome"); ax.set_title(title); ax.set_ylim(0, 1150)
axes[0].set_ylabel(f"counts out of {SHOTS}"); axes[0].legend(frameon=False, loc="upper center", ncol=2)
fig.savefig(OUT / "plus_minus_bases.pdf"); plt.close(fig)
print("[3/7] plus_minus_bases.pdf   direct:", panels[0], " after H:", panels[1])

# Figure 4: the Bloch sphere diagram with the six axis states and one general state
fig = plt.figure(figsize=(5.6, 5.6))
ax = fig.add_subplot(111, projection="3d")
u, v = np.mgrid[0:2 * np.pi:13j, 0:np.pi:7j]
ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="0.88", lw=0.5)
p = np.linspace(0, 2 * np.pi, 200)
ax.plot(np.cos(p), np.sin(p), 0 * p, color=GRAY, lw=0.9)
ax.plot(np.cos(p), 0 * p, np.sin(p), color=GRAY, lw=0.6, ls="--")
axes_pts = {r"$|0\rangle$": (0, 0, 1, 0, 0, 0.14), r"$|1\rangle$": (0, 0, -1, 0, 0, -0.16),
            r"$|+\rangle$": (1, 0, 0, 0.22, 0, -0.06), r"$|-\rangle$": (-1, 0, 0, -0.22, 0, 0.04),
            r"$|{+}i\rangle$": (0, 1, 0, 0.1, 0.3, -0.14), r"$|{-}i\rangle$": (0, -1, 0, 0, -0.26, 0)}
for label, (x, y, z, dx, dy, dz) in axes_pts.items():
    ax.plot([0, x], [0, y], [0, z], color=GRAY, lw=0.8)
    ax.scatter([x], [y], [z], color="k", s=12, depthshade=False)
    ax.text(x + dx, y + dy, z + dz, label, ha="center", va="center", fontsize=11)
theta, phi = np.pi / 3, np.pi / 4
bx, by, bz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
ax.quiver(0, 0, 0, bx, by, bz, color=BLUE, arrow_length_ratio=0.1, lw=2.2)
ax.text(bx + 0.1, by + 0.1, bz + 0.1, r"$|\psi\rangle$", color=BLUE, fontsize=12)
ax.plot([bx, bx], [by, by], [0, bz], color=BLUE, lw=0.8, ls=":")
ax.plot([0, bx], [0, by], [0, 0], color=BLUE, lw=0.8, ls=":")
arc = np.linspace(0, theta, 40)
ax.plot(0.4 * np.sin(arc) * np.cos(phi), 0.4 * np.sin(arc) * np.sin(phi), 0.4 * np.cos(arc), color=BLUE, lw=1.2)
ax.text(0.16, 0.16, 0.5, r"$\theta$", color=BLUE, fontsize=12)
arc2 = np.linspace(0, phi, 40)
ax.plot(0.5 * np.cos(arc2), 0.5 * np.sin(arc2), 0 * arc2, color=BLUE, lw=1.2)
ax.text(0.58, 0.18, -0.12, r"$\phi$", color=BLUE, fontsize=12)
ax.set_xlim(-0.95, 0.95); ax.set_ylim(-0.95, 0.95); ax.set_zlim(-0.95, 0.95)
ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.view_init(elev=22, azim=-55)
fig.savefig(OUT / "bloch_sphere.pdf"); plt.close(fig)
print("[4/7] bloch_sphere.pdf")

# Figure 5: Qiskit's own Bloch plot of the (theta, phi) state, and its expectation values
psi = Statevector([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
fig = plot_bloch_multivector(psi)
fig.savefig(OUT / "bloch_psi_qiskit.pdf"); plt.close(fig)
bv = [psi.expectation_value(Pauli(a)).real for a in "XYZ"]
print("[5/7] bloch_psi_qiskit.pdf   <X>,<Y>,<Z> =", np.round(bv, 3), " formula:", np.round([bx, by, bz], 3))

# Figure 6: the two paths from |0> to |1> through HH and HZH
def path_panel(ax, mid_gate, amps_first, amps_second, title):
    ax.set_xlim(-0.4, 2.5); ax.set_ylim(-0.85, 1.7); ax.set_axis_off(); ax.set_title(title)
    nodes = {(0, 1): r"$|0\rangle$", (1, 1): r"$|0\rangle$", (1, 0): r"$|1\rangle$", (2, 0): r"$|1\rangle$"}
    for (x, y), lab in nodes.items():
        ax.text(x, y, lab, ha="center", va="center", fontsize=11, bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=GRAY, lw=0.8))
    def edge(p, q, label, color, dy):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="->", color=color, lw=1.4, shrinkA=14, shrinkB=14))
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", fontsize=9, color=color)
    edge((0, 1), (1, 1), amps_first[0], BLUE, 0.14)
    edge((0, 1), (1, 0), amps_first[1], ORANGE, -0.26)
    edge((1, 1), (2, 0), amps_second[0], BLUE, 0.14)
    edge((1, 0), (2, 0), amps_second[1], ORANGE, -0.34)
    ax.text(0.5, 1.45, r"first $H$", ha="center", fontsize=9, color=GRAY)
    ax.text(1.5, 1.45, mid_gate, ha="center", fontsize=9, color=GRAY)
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0))
path_panel(axes[0], r"second $H$", [r"$\frac{1}{\sqrt{2}}$", r"$\frac{1}{\sqrt{2}}$"], [r"$\frac{1}{\sqrt{2}}$", r"$-\frac{1}{\sqrt{2}}$"], r"$HH|0\rangle$: the two paths cancel")
path_panel(axes[1], r"$Z$, then second $H$", [r"$\frac{1}{\sqrt{2}}$", r"$\frac{1}{\sqrt{2}}$"], [r"$\frac{1}{\sqrt{2}}$", r"$+\frac{1}{\sqrt{2}}$"], r"$HZH|0\rangle$: the two paths add")
fig.savefig(OUT / "interference_paths.pdf"); plt.close(fig)
hh = QuantumCircuit(1); hh.h(0); hh.h(0); hh.measure_all()
hzh = QuantumCircuit(1); hzh.h(0); hzh.z(0); hzh.h(0); hzh.measure_all()
print("[6/7] interference_paths.pdf   HH counts:", run(hh), " HZH counts:", run(hzh))

# Figure 7: section 9, the four circuits on the simulator and on ibm_kingston
fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.7), sharey=True)
EXACT_FOUR = [{"0": 500, "1": 500}, {"0": 500, "1": 500}, {"0": 1000}, {"1": 1000}]
for ax, label, ex, sc, qcnt in zip(axes, LABELS, EXACT_FOUR, SIM_FOUR, QPU_FOUR):
    b0 = ax.bar([-0.27, 0.73], [ex.get("0", 0), ex.get("1", 0)], 0.26, color=GRAY, label="exact")
    b1 = ax.bar([0.0, 1.0], [sc.get("0", 0), sc.get("1", 0)], 0.26, color=BLUE, label="simulator")
    b2 = ax.bar([0.27, 1.27], [qcnt.get("0", 0), qcnt.get("1", 0)], 0.26, color=ORANGE, label="ibm_kingston")
    ax.bar_label(b1, padding=2, fontsize=6); ax.bar_label(b2, padding=2, fontsize=6)
    ax.set_xticks([0, 1], ["0", "1"]); ax.set_title(label.replace("|+>", r"$|+\rangle$").replace("|->", r"$|-\rangle$").replace("after H", r"after $H$")); ax.set_ylim(0, 1180)
axes[0].set_ylabel(f"counts out of {SHOTS}"); axes[0].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "hardware_four.pdf"); plt.close(fig)
M = np.array([[QPU_FOUR[2]["0"], QPU_FOUR[3]["0"]], [QPU_FOUR[2]["1"], QPU_FOUR[3]["1"]]]) / SHOTS
p_fair = M @ np.array([0.5, 0.5])
mit = [np.linalg.solve(M, np.array([c["0"], c["1"]]) / SHOTS) for c in QPU_FOUR[:2]]
print("[7/7] hardware_four.pdf   readout matrix from circuits 3 and 4 (rows read 0/1, columns prepared 0/1):", np.round(M, 3).tolist())
print("      a fair state would read as P(1) =", round(float(p_fair[1]), 3), "; mitigated P(0) for the direct runs:", [round(float(m[0]), 3) for m in mit])
