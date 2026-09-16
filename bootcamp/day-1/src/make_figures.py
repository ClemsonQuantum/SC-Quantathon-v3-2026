"""Figures and numbers for the Day 1 notes. Run from this folder in the scqv3 env: python make_figures.py

Draws the figures from the numbers the executed solutions notebook printed (September 15, 2026), so the notes
quote exactly what the notebook shows. The simulator counts there are unseeded, so they are copied in as data.
Hardware: ibm_marrakesh (cached in the notebook) and ibm_kingston (the live run recorded in the solutions notebook).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
SEED = 7
SHOTS = 1000
QPU_COUNTS = {"0": 464, "1": 536}          # ibm_marrakesh, 1000 shots (the cached run in the notebook)
LIVE_COUNTS = {"0": 295, "1": 705}         # ibm_kingston, physical qubit 0, 1000 shots, job dakvguc62pvc739q54eg
SIM_COUNTS = {"0": 503, "1": 497}          # AerSimulator, 1000 shots, from the executed solutions notebook
P_AT_NOTEBOOK = {10: 0.700, 100: 0.460, 1000: 0.497, 10000: 0.502}   # section 7.3 of the executed notebook

plt.rcParams.update({
    "font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, ORANGE, GREEN, GRAY = "#1f77b4", "#ff7f0e", "#2ca02c", "0.45"

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
rng = np.random.default_rng(SEED)
def seed():
    return int(rng.integers(2 ** 31 - 1))
sim = AerSimulator()

# Figure 1: the circuit
fig = qc.draw("mpl", style="clifford")
fig.savefig(OUT / "qrng_circuit.pdf"); plt.close(fig)
print("[1/4] qrng_circuit.pdf")

# Figure 2: one simulator run
sim_counts = SIM_COUNTS
fig, ax = plt.subplots(figsize=(3.6, 2.8))
bars = ax.bar(["0", "1"], [sim_counts.get("0", 0), sim_counts.get("1", 0)], color=BLUE, width=0.55)
ax.bar_label(bars, padding=2, fontsize=9)
ax.axhline(SHOTS / 2, ls="--", lw=0.8, color=GRAY)
ax.set_xlabel("outcome"); ax.set_ylabel(f"counts out of {SHOTS}"); ax.set_ylim(0, 620)
fig.savefig(OUT / "qrng_simulator.pdf"); plt.close(fig)
print("[2/4] qrng_simulator.pdf   counts:", sim_counts)

# Figure 3: convergence of the estimate of P(0)
p_at = {}
for n in (10, 100, 1000, 10000):
    c = sim.run(qc, shots=n, seed_simulator=seed()).result().get_counts()
    p_at[n] = c.get("0", 0) / n
shots_list = np.unique(np.logspace(1, 5, 25).astype(int))
errors = []
for n in shots_list:
    c = sim.run(qc, shots=int(n), seed_simulator=seed()).result().get_counts()
    errors.append(abs(c.get("0", 0) / n - 0.5))
fig, ax = plt.subplots(figsize=(4.6, 3.0))
ax.plot(shots_list, errors, "o", ms=4, color=BLUE, alpha=0.55, label=r"$|\hat p - 1/2|$, seeded simulator sweep")
ax.plot(list(P_AT_NOTEBOOK), [abs(v - 0.5) for v in P_AT_NOTEBOOK.values()], "s", ms=6, color=ORANGE, label="the notebook's four runs")
ax.plot(shots_list, 0.5 / np.sqrt(shots_list), "-", color=GRAY, label=r"one standard deviation, $\sqrt{p(1-p)/N}$")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("shots $N$"); ax.set_ylabel("error in the estimate of $P(0)$")
ax.legend(frameon=False, loc="lower left")
fig.savefig(OUT / "shots_convergence.pdf"); plt.close(fig)
print("[3/4] shots_convergence.pdf   notebook P(0) at 10/100/1000/10000 shots:", P_AT_NOTEBOOK)

# Figure 4: classical coin, simulator, hardware
rng = np.random.default_rng(seed=SEED)
flips = rng.integers(0, 2, size=SHOTS)
coin_counts = {"0": int(np.sum(flips == 0)), "1": int(np.sum(flips == 1))}
rows = [("classical coin", coin_counts, GREEN), ("AerSimulator", sim_counts, BLUE), ("ibm_marrakesh (cached)", QPU_COUNTS, ORANGE), ("ibm_kingston (live)", LIVE_COUNTS, "#d62728")]
x = np.arange(2); w = 0.2
fig, ax = plt.subplots(figsize=(5.6, 3.1))
for i, (label, counts, color) in enumerate(rows):
    b = ax.bar(x + (i - 1.5) * w, [counts.get(k, 0) for k in "01"], w, label=label, color=color)
    ax.bar_label(b, padding=2, fontsize=8)
ax.axhline(SHOTS / 2, ls="--", lw=0.8, color=GRAY)
ax.set_xticks(x, ["0", "1"]); ax.set_xlabel("outcome"); ax.set_ylabel(f"counts out of {SHOTS}"); ax.set_ylim(0, 800)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2), ncol=2, fontsize=8)
fig.savefig(OUT / "classical_sim_hardware.pdf"); plt.close(fig)
sigma = np.sqrt(SHOTS * 0.25)
print("[4/4] classical_sim_hardware.pdf   coin:", coin_counts, " sim:", sim_counts, " marrakesh:", QPU_COUNTS, " kingston:", LIVE_COUNTS)
print("      deviations of the count of 0 from 500, in sigma:",
      {name: round(abs(c["0"] - 500) / sigma, 2) for name, c, _ in rows})
