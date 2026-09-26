"""
model.py  --  THIS IS THE ONLY FILE YOUR TEAM NEEDS TO EDIT.

Implement the two methods below. The harness (run.py) takes care of finding
circuits, decompressing them, timing you, and writing the submission file.

Contract
--------
  RuntimeModel()                      load your trained model / weights
  .featurize(qasm_text)   -> dict     parse one circuit into features  (once per circuit)
  .predict(features, thr) -> seconds  predict runtime in seconds       (once per (circuit, threshold))

Rules of the challenge (see README):
  * featurize and predict must each run in <= 15 s per circuit.
  * predict returns a single number: the wall-clock seconds you expect the run to take.
  * There is no separate "timeout" flag. If you think a run will hit the 4-hour cap,
    just predict a duration >= the cap (14400 s). Scoring caps it there for you.

The version below is a trivial BASELINE so the harness runs out of the box.
Replace its guts with your real feature parser and model.
"""

import re

CAP_SECONDS = 4 * 60 * 60  # 4-hour timeout cap


class RuntimeModel:
    def __init__(self, artifacts_dir="artifacts"):
        # Load your trained model here, e.g.:
        #   import joblib
        #   self.model = joblib.load(f"{artifacts_dir}/model.pkl")
        self.model = None

    # ------------------------------------------------------------------ #
    # 1) FEATURE PARSER  --  .qasm text  ->  feature dict                 #
    # ------------------------------------------------------------------ #
    def featurize(self, qasm_text: str) -> dict:
        # BASELINE: a few cheap structural features. Design your own.
        n_qubits = 0
        for m in re.finditer(r"q(?:u)?(?:reg|bit)\s+\w+\s*\[\s*(\d+)\s*\]", qasm_text):
            n_qubits += int(m.group(1))

        lines = [l.strip() for l in qasm_text.splitlines()]
        gate_lines = [l for l in lines if l and not l.startswith(("//", "OPENQASM",
                     "include", "qreg", "creg", "qubit", "bit", "gate"))]
        n_ops = len(gate_lines)
        # crude two-qubit-gate count (entangling ops dominate simulator cost)
        n_2q = len(re.findall(r"\b(cx|cz|cy|ch|swap|iswap|rzz|rxx|ryy|cp|crx|cry|crz|ecr)\b", qasm_text))

        return {"n_qubits": n_qubits, "n_ops": n_ops, "n_2q": n_2q}

    # ------------------------------------------------------------------ #
    # 2) MODEL  --  (features, threshold)  ->  predicted seconds          #
    # ------------------------------------------------------------------ #
    def predict(self, features: dict, threshold: int) -> float:
        # BASELINE: a toy formula. Replace with your trained model.
        n = features["n_qubits"]
        est = 1e-4 * (2 ** min(n, 30)) * (1 + features["n_2q"] / 1000.0)
        est *= (threshold / 16.0) ** 0.5           # crude threshold scaling
        # predict >= cap to signal "this will time out"
        return float(min(est, CAP_SECONDS))
