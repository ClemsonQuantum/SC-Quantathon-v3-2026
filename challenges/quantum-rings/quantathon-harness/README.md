# Quantathon — Submission Harness

Predict how long each circuit takes to simulate, straight from the `.qasm` file.
This harness produces the **one file you send back to us**.

## Setup (once)

```bash
pip install -r requirements.txt
```

## What you edit

**Only `model.py`.** Implement these methods:

| Method | Job | Called |
|---|---|---|
| `RuntimeModel()` | load your trained model | once |
| `featurize(qasm_text)` | parse a circuit into features | once per circuit |
| `predict(features, threshold)` | return **predicted seconds** (one number) | once per (circuit, threshold) |

There is no timeout flag — if you think a run will time out, just predict a duration
**≥ the 4-hour cap (14400 s)**.

A trivial baseline is already in `model.py` so the harness runs before you touch
anything. Replace its body with your real parser and model.

**Caps:** `featurize` and `predict` must each run in **≤ 15 s per circuit**. The
harness times you and warns on anything over.

## What's included

| Path | Contents |
|---|---|
| `circuits/` | the training circuits, one `<id>.qasm.zst` per circuit |
| `runtime-data.csv` | training labels, one row per `(circuit, threshold)` run |

The circuits are `zstd`-compressed. `run.py` decompresses them for you, so you
don't need raw files to run the harness. To get raw `.qasm` files for exploring
and training, see
[Getting the raw `.qasm` files](../README.md#getting-the-raw-qasm-files) in the
main README. Decompress them **outside** `circuits/`, or the harness will read
each circuit twice.

## Run it

1. `circuits/` already holds the training circuits. In the final hours we DM you
   the hold-out circuits: put them in `circuits/` too (`.qasm` or `.qasm.zst`,
   subfolders are fine). Only hold-out runs are scored, so you can remove the
   training circuits first to make the run faster.
2. Generate your submission:

```bash
python run.py --team "Your Team Name"
```

This writes **`submission.csv`**:

```
team,filename,threshold,pred_duration_s,parse_s,predict_s
```

3. **DM `submission.csv` back to us.** That's your entry.

## Check your score first (optional but recommended)

You have the training labels (`runtime-data.csv`). Run `run.py` on the training
circuits, then score yourself with the *exact* metric we use:

```bash
python score.py --pred submission.csv --labels runtime-data.csv
```

## How the automated third is scored

Your total score is **1/3 automated + 2/3 subjective** (presentation, novelty,
process, etc. — judged live, five equally-weighted categories). The automated third
is **pure duration accuracy**, per `(circuit, threshold)`:

```
score = max(0, 1 − |log10(pred / actual)| / 2)      # exact = 1.0, off by 10× = 0
```

Runtimes span seconds to hours, so accuracy is measured in **log scale** — being
2× off costs the same whether the run is 1 second or 1 hour. Timeout circuits are
scored against the 4-hour cap, so predicting ≥ cap earns full credit on them and
predicting seconds for one is penalized like any other large miss.

Your score is the average over **every** hold-out run. A run missing from your
`submission.csv` scores 0, so make sure every circuit gets a prediction.

## Rules

- Build your own parser; no starter feature list is provided.
- You must be able to explain every part of your submission.
- Don't try to recover the source algorithm from filenames/metadata.
