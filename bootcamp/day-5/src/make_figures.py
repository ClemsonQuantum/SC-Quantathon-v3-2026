"""Figures and numbers for the Day 5 notes. Run from this folder in the scqv3 env: python make_figures.py

Draws the figures from the values of the executed solutions notebook (notebook_values.json, written by
docs/build/dump_vars.py), saves vector figures to figures/, and prints the numbers quoted in notes.tex. The device counts are Day 4's recorded run on
ibm_kingston (Heron r2, physical qubits 55 and 59, 1000 shots).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.quantum_info import hellinger_fidelity
from qiskit.primitives import StatevectorSampler
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke, FakeManilaV2

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
SHOTS = 1000
SEED = 7
REAL = {"00": 512, "11": 478, "01": 6, "10": 4}      # Day 4 run on ibm_kingston (Heron r2), physical qubits 55 and 59, 1000 shots
import json
NB = json.load(open(Path(__file__).parent / "notebook_values.json"))     # the executed solutions notebook's variables
rng = np.random.default_rng(SEED)
def seed():
    return int(rng.integers(2 ** 31 - 1))

plt.rcParams.update({
    "font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, ORANGE, GREEN, GRAY = "#1f77b4", "#ff7f0e", "#2ca02c", "0.45"

backend = FakeSherbrooke()
target, props = backend.target, backend.properties()
gate = [g for g in target.operation_names if g in ("ecr", "cz", "cx")][0]
n = backend.num_qubits
t1 = np.array([props.t1(q) for q in range(n)]) * 1e6
t2 = np.array([props.t2(q) for q in range(n)]) * 1e6
ro = np.array([props.readout_error(q) for q in range(n)])
gerr = {p: target[gate][p].error for p in target[gate]}
gdur = {p: target[gate][p].duration for p in target[gate]}
edges = backend.coupling_map.get_edges()
print(f"[machine] {backend.name}: {n} qubits, {len({tuple(sorted(e)) for e in edges})} coupled pairs, 2q gate {gate}")
print(f"          median T1 {np.median(t1):.0f} us, T2 {np.median(t2):.0f} us, readout {np.median(ro):.2%}; "
      f"{gate} median error {np.median(list(gerr.values())):.2%}, worst {max(gerr.values()):.1%}, duration {np.median(list(gdur.values()))*1e9:.0f} ns")
bp = min(gerr, key=gerr.get); print(f"          best pair {bp}: {gerr[bp]:.3%}; qubit 0: T1 {t1[0]:.0f} us, T2 {t2[0]:.0f} us, readout {ro[0]:.2%}")

# Figure 1: calibration data across the chip
fig, axes = plt.subplots(1, 3, figsize=(9, 2.6))
axes[0].hist(t1, bins=25, color=BLUE); axes[0].set_xlabel("T1 (us)"); axes[0].set_ylabel("qubits")
axes[1].hist(ro * 100, bins=25, color=ORANGE); axes[1].set_xlabel("readout error (%)")
axes[2].hist(np.array(list(gerr.values())) * 100, bins=25, color=GREEN); axes[2].set_xlabel(f"{gate} gate error (%)")
fig.tight_layout(); fig.savefig(OUT / "calibration.pdf"); plt.close(fig)
print("[1/8] calibration.pdf")

# Transpilation numbers
bell = QuantumCircuit(2); bell.h(0); bell.cx(0, 1); bell.measure_all()
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
bell_isa = pm.run(bell)
print(f"[transpile] Bell: {dict(bell.count_ops())} depth {bell.depth()} -> {dict(bell_isa.count_ops())} depth {bell_isa.depth()}, physical {bell_isa.layout.final_index_layout()}")
def ghz(k):
    qc = QuantumCircuit(k); qc.h(0)
    for q in range(k - 1): qc.cx(q, q + 1)
    qc.measure_all(); return qc
for level in range(4):
    isa = generate_preset_pass_manager(optimization_level=level, backend=backend, seed_transpiler=1).run(ghz(5))
    ops = isa.count_ops()
    print(f"            GHZ(5) level {level}: depth {isa.depth()}, {gate} {ops.get(gate,0)}, gates {sum(v for k,v in ops.items() if k not in ('measure','barrier'))}")
manila = FakeManilaV2()
star = QuantumCircuit(5); star.h(0)
for q in range(1, 5): star.cx(0, q)
star.measure_all()
star_isa = generate_preset_pass_manager(optimization_level=3, backend=manila, seed_transpiler=1).run(star)
print(f"            star on Manila line: cx {star_isa.count_ops().get('cx',0)} for 4 logical CNOTs, depth {star_isa.depth()}")

# Figure 2: decoherence curves for qubit 0
T1, T2 = props.t1(0), props.t2(0)
waits = np.linspace(0, 3 * T1, 13)
def idle(prep, wait, xb=False):
    qc = QuantumCircuit(1)
    for g in prep: getattr(qc, g)(0)
    qc.append(thermal_relaxation_error(T1, T2, wait).to_instruction(), [0])
    if xb: qc.h(0)
    qc.measure_all()
    return AerSimulator().run(qc, shots=SHOTS, seed_simulator=seed()).result().get_counts()
waits = np.array(NB["waits"]); p1 = NB["p1_survive"]; pp = NB["p_plus"]           # the notebook's own runs
fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.7))
axes[0].plot(waits * 1e6, p1, "o", color=BLUE, label="simulated, 1000 shots"); axes[0].plot(waits * 1e6, np.exp(-waits / T1), "-", color=GRAY, label=r"$e^{-t/T_1}$")
axes[0].set_xlabel("idle time (us)"); axes[0].set_ylabel(r"$P(1)$ after preparing $|1\rangle$"); axes[0].set_title(f"$T_1$ = {T1*1e6:.0f} us"); axes[0].legend(frameon=False)
axes[1].plot(waits * 1e6, pp, "o", color=ORANGE, label="simulated, 1000 shots"); axes[1].plot(waits * 1e6, 0.5 * (1 + np.exp(-waits / T2)), "-", color=GRAY, label=r"$\frac{1}{2}(1+e^{-t/T_2})$")
axes[1].set_xlabel("idle time (us)"); axes[1].set_ylabel(r"$P(+)$ after preparing $|+\rangle$"); axes[1].set_title(f"$T_2$ = {T2*1e6:.0f} us"); axes[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(OUT / "decoherence.pdf"); plt.close(fig)
print("[2/8] decoherence.pdf")

# Figure 3: CNOT repetition under depolarizing noise
p_gate = 0.01
nm = NoiseModel(); nm.add_all_qubit_quantum_error(depolarizing_error(p_gate, 2), ["cx"])
noisy_cx = AerSimulator(noise_model=nm)
ks = np.arange(0, 41, 4); surv = []
for k in ks:
    qc = QuantumCircuit(2)
    for _ in range(k): qc.cx(0, 1)
    qc.measure_all(); surv.append(noisy_cx.run(qc, shots=SHOTS, seed_simulator=seed()).result().get_counts().get("00", 0) / SHOTS)
ks, surv = np.array(NB["ks"]), NB["survival"]                                       # the notebook's own run
fig, ax = plt.subplots(figsize=(4.6, 2.8))
ax.plot(ks, surv, "o", color=BLUE, label=f"{p_gate:.0%} depolarizing error per CNOT")
ax.plot(ks, 0.25 + 0.75 * (1 - p_gate) ** ks, "-", color=GRAY, label=r"$\frac{1}{4} + \frac{3}{4}(1 - p)^k$")
ax.set_xlabel("number of CNOTs $k$"); ax.set_ylabel("$P(00)$"); ax.legend(frameon=False)
fig.savefig(OUT / "cnot_decay.pdf"); plt.close(fig)
print(f"[3/8] cnot_decay.pdf   survival at k = 0, 20, 40: {surv[0]:.3f}, {surv[5]:.3f}, {surv[-1]:.3f}")

# Figure 4: Bell state three ways
noisy = AerSimulator.from_backend(backend)
ideal, sim = NB["bell_ideal"], NB["bell_noisy"]                                      # the notebook's own runs
def imp(c): return (c.get("01", 0) + c.get("10", 0)) / sum(c.values())
rows = [("ideal simulator", ideal, BLUE), ("noisy simulator", sim, GREEN), ("real device", REAL, ORANGE)]
keys = ["00", "01", "10", "11"]; x = np.arange(4); w = 0.26
fig, ax = plt.subplots(figsize=(5.4, 3.0))
for i, (label, c, color) in enumerate(rows):
    tot = sum(c.values()); b = ax.bar(x + (i - 1) * w, [c.get(k, 0) / tot * 100 for k in keys], w, label=label, color=color)
    ax.bar_label(b, labels=[f"{c.get(k, 0)/tot*100:.1f}" for k in keys], padding=2, fontsize=7)
ax.set_xticks(x, keys); ax.set_xlabel("outcome"); ax.set_ylabel("percent of shots"); ax.set_ylim(0, 60)
ax.legend(frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.15))
fig.savefig(OUT / "bell_three_ways.pdf"); plt.close(fig)
for label, c, _ in rows: print(f"[4/8] {label:<16} {c}  impossible {imp(c):.1%}  fidelity {hellinger_fidelity(ideal, c):.3f}")

# Figure 5: readout mitigation
phys = bell_isa.layout.final_index_layout()
pm_cal = generate_preset_pass_manager(optimization_level=0, backend=backend, initial_layout=phys)
M = np.zeros((4, 4))
for j, lab in enumerate(keys):
    qc = QuantumCircuit(2)
    for q, bit in enumerate(reversed(lab)):
        if bit == "1": qc.x(q)
    qc.measure_all()
    c = noisy.run(pm_cal.run(qc), shots=SHOTS, seed_simulator=seed()).result().get_counts()
    for i, out in enumerate(keys): M[i, j] = c.get(out, 0) / SHOTS
M = np.array(NB["M"])                                                              # the notebook's own calibration
p_meas = np.array([sim.get(k, 0) for k in keys], float) / SHOTS
p_true = np.clip(np.linalg.solve(M, p_meas), 0, None); p_true /= p_true.sum()
fig, ax = plt.subplots(figsize=(4.6, 2.8))
b1 = ax.bar(x - 0.18, p_meas * 100, 0.36, label="noisy simulator, raw", color=GREEN)
b2 = ax.bar(x + 0.18, p_true * 100, 0.36, label="after readout mitigation", color=BLUE)
ax.bar_label(b1, labels=[f"{v*100:.1f}" for v in p_meas], padding=2, fontsize=7); ax.bar_label(b2, labels=[f"{v*100:.1f}" for v in p_true], padding=2, fontsize=7)
ax.set_xticks(x, keys); ax.set_xlabel("outcome"); ax.set_ylabel("percent"); ax.set_ylim(0, 60); ax.legend(frameon=False, loc="upper center")
fig.savefig(OUT / "readout_mitigation.pdf"); plt.close(fig)
print(f"[5/8] readout_mitigation.pdf   physical qubits {phys}, M diag {np.round(np.diag(M),3)}, impossible raw {imp(sim):.1%} -> mitigated {(p_true[1]+p_true[2]):.1%}")
print("      M =\n", np.round(M, 3))

# Figure 6: zero-noise extrapolation
zne_nm = NoiseModel(); zne_nm.add_all_qubit_quantum_error(depolarizing_error(0.03, 2), ["cx"])
zne_sim = AerSimulator(noise_model=zne_nm)
def folded(k):
    qc = QuantumCircuit(2); qc.h(0)
    for _ in range(k): qc.cx(0, 1)
    qc.measure_all(); return qc
def zz(c):
    tot = sum(c.values()); return sum(v * (1 if k in ("00", "11") else -1) for k, v in c.items()) / tot
scales = np.array(NB["noise_scales"]); vals = NB["zz_values"]                       # the notebook's own run
lin, quad = np.polyfit(scales, vals, 1), np.polyfit(scales, vals, 2)
lam = np.linspace(0, 5.5, 60)
fig, ax = plt.subplots(figsize=(4.6, 2.8))
ax.plot(scales, vals, "o", ms=7, color=BLUE, label="measured")
ax.plot(lam, np.polyval(lin, lam), "-", color=ORANGE, label=f"linear fit, {np.polyval(lin, 0):.3f} at 0")
ax.plot(lam, np.polyval(quad, lam), "--", color=GREEN, label=f"quadratic fit, {np.polyval(quad, 0):.3f} at 0")
ax.axhline(1, color=GRAY, lw=0.8); ax.set_xlabel(r"noise scale $\lambda$"); ax.set_ylabel(r"$\langle ZZ\rangle$"); ax.legend(frameon=False, loc="lower left")
fig.savefig(OUT / "zne.pdf"); plt.close(fig)
print(f"[6/8] zne.pdf   <ZZ> at scales {scales}: {np.round(vals,4)}; linear -> {np.polyval(lin,0):.4f}, quadratic -> {np.polyval(quad,0):.4f}")

# Figure 7: a one-qubit circuit before and after translation to the native gate set (section 3)
qc = QuantumCircuit(1); qc.h(0); qc.t(0); qc.h(0)
pm_native = generate_preset_pass_manager(optimization_level=1, basis_gates=["rz", "sx", "x", "cx"])
native = pm_native.run(qc)
fig = qc.draw("mpl", style="clifford"); fig.savefig(OUT / "hth_circuit.pdf"); plt.close(fig)
fig = native.draw("mpl", style="clifford"); fig.savefig(OUT / "hth_native.pdf"); plt.close(fig)
print("[7/8] hth_circuit.pdf, hth_native.pdf   native gates:", dict(native.count_ops()), " depth", qc.depth(), "->", native.depth())

# Figure 8: the live run of section 8 (ibm_kingston, physical qubits 55 and 59, jobs dal2f4elg97s73c8frv0 and dal2f4gnf91c73crl5sg)
LIVE_COUNTS = {"00": 527, "11": 463, "10": 4, "01": 6}
LIVE_M_DIAG = [0.999, 0.985, 0.995, 0.992]
LIVE_MITIGATED = {"00": 0.527, "01": 0.005, "10": 0.001, "11": 0.467}
ZZ = [("exact", 1.0), ("snapshot ZNE", 0.9995), ("device, raw", 0.9800), ("device, readout\nmitigated", 0.9884), ("device, runtime\nTREX + ZNE", 0.9952)]
fig, ax = plt.subplots(figsize=(5.6, 2.9))
b = ax.bar([z[0] for z in ZZ], [z[1] for z in ZZ], color=[GRAY, GREEN, ORANGE, BLUE, BLUE], width=0.6)
ax.bar_label(b, labels=[f"{z[1]:.4f}" for z in ZZ], padding=2, fontsize=8)
ax.set_ylim(0.95, 1.01); ax.axhline(1, color=GRAY, lw=0.8); ax.set_ylabel(r"$\langle ZZ\rangle$ of the Bell state"); ax.tick_params(axis="x", labelsize=8)
fig.savefig(OUT / "live_zz.pdf"); plt.close(fig)
print("[8/8] live_zz.pdf   live counts", LIVE_COUNTS, "impossible", f"{imp(LIVE_COUNTS):.1%}", "fidelity", f"{hellinger_fidelity(ideal, LIVE_COUNTS):.3f}")
