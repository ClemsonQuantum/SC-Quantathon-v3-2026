#!/usr/bin/env python3
"""
run.py  --  Quantathon submission harness (DO NOT EDIT for your submission).

What it does:
  1. Scans a circuits directory for .qasm and .qasm.zst files.
  2. Decompresses .zst automatically.
  3. Calls your model (model.py): featurize once per circuit, predict once per
     (circuit, threshold).
  4. Times your parser and model, enforces the per-circuit caps.
  5. Writes a standardized submission.csv you DM back to the organizers.

Usage:
  python run.py --team "My Team Name"
  python run.py --team "My Team" --circuits circuits --thresholds 16,64,512 --out submission.csv

You should not need to change anything here. Edit model.py only.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from model import RuntimeModel

PARSE_CAP_S = 15.0     # per-circuit feature-parsing cap
PREDICT_CAP_S = 15.0   # per-circuit inference cap


def read_qasm(path: Path) -> str:
    """Return QASM text for a .qasm or .qasm.zst file."""
    if path.suffix == ".zst":
        try:
            import zstandard as zstd
            with open(path, "rb") as f:
                return zstd.ZstdDecompressor().stream_reader(f).read().decode("utf-8", "replace")
        except ImportError:
            import subprocess
            out = subprocess.run(["zstd", "-dc", str(path)], capture_output=True)
            if out.returncode != 0:
                raise RuntimeError(
                    f"Could not decompress {path.name}. Install the python package "
                    f"'zstandard' (pip install zstandard) or the 'zstd' CLI."
                )
            return out.stdout.decode("utf-8", "replace")
    return path.read_text(encoding="utf-8", errors="replace")


def find_circuits(circuits_dir: Path):
    files = sorted(p for p in circuits_dir.rglob("*")
                   if p.suffix in (".qasm", ".zst") and p.is_file())
    if not files:
        sys.exit(f"No .qasm / .qasm.zst files found under {circuits_dir}/")
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", required=True, help="Your team name (appears in the output).")
    ap.add_argument("--circuits", default="circuits", help="Directory of circuit files.")
    ap.add_argument("--thresholds", default="16,64,512",
                    help="Comma-separated thresholds to predict for.")
    ap.add_argument("--out", default="submission.csv")
    args = ap.parse_args()

    thresholds = [int(t) for t in args.thresholds.split(",") if t.strip()]
    circuits = find_circuits(Path(args.circuits))
    model = RuntimeModel()

    rows = []
    over_cap = []
    print(f"Scoring {len(circuits)} circuits x {len(thresholds)} thresholds "
          f"= {len(circuits)*len(thresholds)} predictions ...")

    for i, path in enumerate(circuits, 1):
        name = path.name[:-4] if path.suffix == ".zst" else path.name  # strip .zst -> .qasm
        try:
            qasm = read_qasm(path)
        except Exception as e:
            print(f"  ! {path.name}: read failed ({e})")
            continue

        t0 = time.perf_counter()
        try:
            feats = model.featurize(qasm)
        except Exception as e:
            print(f"  ! {path.name}: featurize crashed ({e})")
            continue
        parse_s = time.perf_counter() - t0
        if parse_s > PARSE_CAP_S:
            over_cap.append((name, "parse", round(parse_s, 2)))

        for thr in thresholds:
            t1 = time.perf_counter()
            try:
                dur = model.predict(feats, thr)
            except Exception as e:
                print(f"  ! {path.name}@{thr}: predict crashed ({e})")
                continue
            predict_s = time.perf_counter() - t1
            if predict_s > PREDICT_CAP_S:
                over_cap.append((name, f"predict@{thr}", round(predict_s, 2)))
            rows.append({
                "team": args.team,
                "filename": name,
                "threshold": thr,
                "pred_duration_s": f"{float(dur):.6f}",
                "parse_s": f"{parse_s:.4f}",
                "predict_s": f"{predict_s:.4f}",
            })
        if i % 25 == 0 or i == len(circuits):
            print(f"  {i}/{len(circuits)} circuits done")

    fields = ["team", "filename", "threshold", "pred_duration_s",
              "parse_s", "predict_s"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.out}")
    if over_cap:
        print(f"WARNING: {len(over_cap)} runs exceeded the 15 s cap "
              f"(these may be penalized). First few: {over_cap[:5]}")
    print("DM this file to the organizers.")


if __name__ == "__main__":
    main()
