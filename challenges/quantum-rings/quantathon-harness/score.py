#!/usr/bin/env python3
"""
score.py  --  self-test your submission on the TRAINING labels.

The organizers score the hidden hold-out with this exact metric, so you can use
it on the training set to estimate your automated score before you submit.

Usage:
  python score.py --pred submission.csv --labels runtime-data.csv

Metric (the automated 1/3 of the total score) -- pure duration accuracy:
  For each (circuit, threshold):
      actual = measured runtime, or the 4-hour cap (14400 s) if it timed out
      pred   = your predicted seconds (capped at 14400 s on timeout rows)
      score  = max(0, 1 - |log10(pred / actual)| / 2)     # exact = 1.0, off by 10x = 0
  Automated % = average score over ALL labeled runs. A labeled run with no
  prediction in your submission scores 0, so skipping circuits never helps.

There is no separate timeout metric: to "predict a timeout", predict a duration
>= the cap (that earns full credit on a timeout row); predicting seconds for a
circuit that actually timed out takes the normal log-error hit.
"""

import argparse
import csv
import math

L = 2.0
CAP = 14400.0


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader((line.replace("\r\n", "\n") for line in f)))


def key(row):
    return (row["filename"].strip(), int(float(row["threshold"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="submission.csv")
    ap.add_argument("--labels", default="runtime-data.csv")
    args = ap.parse_args()

    preds = {key(r): r for r in load_csv(args.pred)}
    labels = load_csv(args.labels)

    scores = []
    matched = 0
    missing = 0
    for lab in labels:
        k = key(lab)
        is_timeout = lab.get("status", "").strip().lower() == "timeout"
        if is_timeout:
            actual = CAP
        else:
            d = lab.get("duration_s", "").strip()
            if not d:
                continue
            actual = float(d)
        if actual <= 0:
            continue
        if k not in preds:
            missing += 1
            scores.append(0.0)
            continue
        matched += 1
        pred = float(preds[k]["pred_duration_s"])
        if is_timeout:
            pred = min(pred, CAP)
        pred = max(pred, 1e-9)
        scores.append(max(0.0, 1.0 - abs(math.log10(pred / actual)) / L))

    if matched == 0:
        raise SystemExit("No overlap between submission and labels. Check filenames/thresholds.")
    automated = sum(scores) / len(scores) if scores else 0.0
    print(f"Scored runs    : {len(scores)}")
    print(f"Predicted      : {matched}")
    print(f"Missing (= 0)  : {missing}")
    print(f"AUTOMATED SCORE (duration accuracy, = 1/3 of total): {automated:6.2%}")


if __name__ == "__main__":
    main()
