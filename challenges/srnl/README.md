# SC Quantathon V3 — SRNL Earthquake-Q Forecasting Challenge

Forecast the chance of an earthquake near every cell on the map, 30 days at a time, from raw geophysical data, with probabilities you can defend.


## Contents

- [Overview](#overview)
- [Timeline](#timeline)
- [The task](#the-task)
- [Dataset](#dataset)
- [Starter notebook](#starter-notebook)
- [What you build](#what-you-build)
- [Judging & scoring](#judging--scoring)
- [Submission](#submission)
- [Rules](#rules)
- [Pathways](#pathways)
- [Resources](#resources)

## Overview

A damaging earthquake has just struck. Buildings and infrastructure are down, and
aftershocks within the damage zone (about 100 km) could destabilize it further. Two
groups are waiting on your forecast:

- **Emergency response crews** need a **30-day** look-ahead: when is it safe to enter
  the damage zone and begin life-saving operations with acceptable risk?
- **Infrastructure repair crews** need a **6-month** look-ahead: when can they be
  mobilized?

You have just over 24 hours to build the best, most honest forecast you can from five
raw geophysical data streams, and to brief the stakeholders on it.

Per the USGS, no scientist has ever predicted a major earthquake. What science can do is
estimate the probability of one in a given area over a given time. That is why your
output is a **probability**, not a prediction.

- **Open-ended.** There is no single right answer. The pathway is yours to discover.
- **Hands-on.** You build everything from raw data, with a starter notebook as the baseline.
- **Honest.** Forecasts you can defend are rewarded, not the best-looking number.

Sponsored by [Savannah River National Laboratory](https://www.srnl.gov/). Challenge
developed by Larry M. Deschaine, PhD, Quantum AI instructor, SRNL & Clemson University.
**Winning prize:** co-authoring a journal paper.

## Timeline

| Milestone | When |
|---|---|
| Kickoff — data, starter notebook, and decks released | 10am 9/26 |
| Submissions close on Devpost | 10am 9/27 |
| Judging presentations | 12pm 9/27 |
| Results | 6pm 9/27 |

Competition is **team-based**. Division of labor is up to you.

## The task

For each grid cell and each 30-day window, forecast:

> What is the probability that **at least one earthquake of magnitude ≥ 2.0** occurs
> **within 100 km** of the cell during the window?

- **Output:** a calibrated probability in [0, 1] for every cell-window. Not a yes/no, not
  a magnitude, not a time.
- **Grid:** half-degree cells across the central and eastern United States.
- **Windows:** consecutive 30-day windows, forecast forward from a fixed information
  cutoff.
- **Input:** anything in the supplied data that was known **before** the forecast's
  issue time, and nothing after it (see [Rules](#rules)).

Qualifying earthquakes are rare, so this is a **calibration problem**, not a guessing
game: when you say 20%, it should happen about 20% of the time.

## Dataset

Three CSV files in [`Data/`](Data/), split by time. All three share one long format.

| File | Time span | Rows | Earthquakes | Use it for |
|---|---|---|---|---|
| [`earthquakeq_train.csv`](Data/earthquakeq_train.csv) | 1990–2021 | 271,207 | 11,597 | Fitting your models |
| [`earthquakeq_test.csv`](Data/earthquakeq_test.csv) | 2022–2024 | 48,328 | 2,027 | Tuning and model selection |
| [`earthquakeq_judge.csv`](Data/earthquakeq_judge.csv) | Jan 2025–Mar 2026 | 17,979 | 740 | **Final self-check** — treat it as sealed while you build |

The judge window stands in for the future. In a real deployment you would never see it;
for the Quantathon it is handed to you up front, so use it once, at the end, for an
honest check.

### Sources

Each row is one observation from one of five sources. The seismic catalog is the signal
you are forecasting. The other four streams are candidate drivers; whether they help is
for you to find out.

| Source | Fields / parameters | Cadence | What it is |
|---|---|---|---|
| `seismic` | `time`, `latitude`, `longitude`, `depth_km`, `magnitude` | per event | USGS earthquake catalog, events M ≥ 1.0. **This is the signal.** |
| `geomagnetic` | `ap`, `kp` | daily | Geomagnetic activity indices (GFZ) |
| `solar` | `f107_observed`, `sunspot_number` | daily | Solar radio flux and sunspot number (GFZ) |
| `tidal_ephemeris` | `tidal_potential`, `lunar_phase` | daily | Earth tides: small periodic stresses |
| `gps` | `east_m`, `north_m`, `up_m` | daily, 18 stations | GNSS station positions: crustal strain near fault zones |

### Format

One row per observation, same columns in every file:

```
source,time,latitude,longitude,depth_km,magnitude,station_id,parameter,value
```

- `seismic` rows fill `time`, `latitude`, `longitude`, `depth_km`, `magnitude`.
- The four driver streams fill `time`, `parameter`, `value` (e.g. `parameter=ap`,
  `value=16.0`). `station_id` is set only for `gps`.

## Starter notebook

[`Earthquake-Q Classical Starter.ipynb`](Earthquake-Q%20Classical%20Starter.ipynb) is
the common starting line every team gets. Fully offline, it:

1. **Reads** the three CSVs and pulls out the seismic catalog.
2. **Builds** the forecasting target as (cell, issue-date) examples, with a handful of
   leakage-safe seismicity features: nearby event counts over 7 / 30 / 90 / 365 days,
   days since the last nearby event, and the cell's latitude and longitude.
3. **Trains** one gradient-boosted classifier (LightGBM, or scikit-learn's
   `HistGradientBoostingClassifier` if LightGBM is missing) and calibrates it with
   isotonic regression on the test split.
4. **Reports** a scorecard (AUC, PR-AUC, information gain, Brier, ECE) plus ROC,
   precision–recall, and reliability plots on the judge split.

It is **plain on purpose**: it uses only the seismic stream and ignores the other four.
Run it first, understand it, then make it better.

### Running it

The CSVs live in `Data/`, so point the notebook there in section 1:

```python
DATA_DIR = Path("Data")
```

Building the training examples is the slow step, about 1–2 minutes.

## What you build

| Deliverable | What it is |
|---|---|
| **Forecast** | A probability for every scored cell-window, in the format the starter notebook produces. |
| **Code** | The notebook or scripts that build your forecast, so the judges can see how you did it. |
| **Write-up** | A short account of what you tried, what worked, what didn't, and, honestly, how well it did on your held-out check. |

**Build something you can defend.** There is no answer key to reverse-engineer.

## Judging & scoring

Skill and honesty, not accuracy.

| Metric | What it measures |
|---|---|
| **Information gain** (primary) | How much your forecast beats the base rate, in bits per prediction. Real skill, not guesswork. |
| **Calibration** | Brier score and expected calibration error (ECE). When you say 20%, does it happen about 20% of the time? A confident but wrong forecast scores badly. |
| **Discrimination** | AUC and PR-AUC. Can you rank risky cells above safe ones? A useful check, but not the whole story. |

Information gain compares your forecast's log-loss with that of climatology (the
training base rate), averaged over every prediction:

```
LL(q) = −mean[ y·ln(q) + (1 − y)·ln(1 − q) ]
IG    = [ LL(base rate) − LL(your forecast) ] / ln 2      bits per prediction
```

Positive IG means your forecast carries information the base rate does not. The
starter notebook's `information_gain_bits()` computes it.

**Why not accuracy?** Qualifying earthquakes are rare, so a model that always predicts
"no" is highly accurate and completely useless. The score rewards the information you
add and whether your probabilities are true.

### What earns respect

- **Skill with calibration** — probabilities that are both informative and true.
- **A clean held-out story** — your judge score is close to your test score (no leaks).
- **Clarity about uncertainty** — you know what you know, and say so.
- **Honesty** — if the simple approach won, say so, with evidence. If not, show how
  your extra analysis lets rescue operations begin as soon as it is safe.

## Submission

One Devpost submission per team, due **Sunday, September 27 at 10:00 AM**. Include your
forecast, code, and write-up (see [What you build](#what-you-build)). The
[Devpost rules](https://sc-quantathon-v3.devpost.com/rules) give the ZIP layout and
what else to include. Teams present to the judges at noon on Sunday.

## Rules

- **The one rule that matters: never let the future leak into the past.** Every feature
  for a forecast must use only information available before that forecast's issue
  time. The tell: if your judge score is far worse than your own test score, you have
  leaked.
- **Split by time.** Train on the past, calibrate on later held-out data, evaluate on
  later data still. Never shuffle a time series.
- **Treat the judge split as sealed.** Build and tune on train and test; use judge once,
  for your final honest check.
- **Train the way you are scored:** on a grid, at an issue time, looking only forward.
- **Teams.** Team-based; the work split is up to you.
- **Own your solution.** You must understand and be able to explain everything you
  submit.
- **Build inside the window.** All project code is written during the hacking window.

## Pathways

Where you might take it. No pathway is required, and none is guaranteed to win.

| Pathway | Ideas |
|---|---|
| **Better features** | Richer seismicity: b-values, event-rate acceleration, multi-radius and multi-window counts, recency. What does geography miss? |
| **The other streams** | Geomagnetic, solar, tidal, GPS. Do they carry signal? Prove it from the data; don't assume it. |
| **Physics** | Aftershock-triggering models such as ETAS are classic. Feeding physics into your model is a strong move. |
| **Quantum** | Encodings, kernels, variational classifiers. Explore where quantum can contribute. |

The interesting result might be that a simple approach is hard to beat. If so, show it,
with the numbers.

### Questions worth asking

- Is there enough data? Is it the right data? Is it split right?
- Classical, quantum, or hybrid?
- Certainty versus uncertainty: when should rescue operations begin? What is the safety
  margin, and how do you present it to stakeholders?
- The starter drops events below a magnitude of completeness `MC = 1.75`. Is that the
  right cut? Estimating it well is part of the craft.
- Could your forecast become a map on an emergency response website, where a
  coordinator clicks an epicenter and instantly sees the risk of significant aftershocks?

## Resources

In this folder:

- **[Earthquake-Q Intro Briefing](Earthquake-Q%20Intro%20Briefing.pptx)** — the
  12-slide challenge brief. Read this first.
- **[Earthquake-Q Study Deck](Earthquake-Q%20Study%20Deck.pptx)** — 100 slides in nine
  modules (the problem, the raw data, seismology, feature engineering, validation and
  calibration, quantum methods, and more), with exercises and answer keys. Background
  to get you started, not a gold standard: verify what you use.
- **[Earthquake-Q Classical Starter](Earthquake-Q%20Classical%20Starter.ipynb)** — the
  baseline notebook (see [Starter notebook](#starter-notebook)).

Further reading:

- **Can you predict earthquakes?** — USGS FAQ on prediction versus probabilistic
  forecasting — <https://www.usgs.gov/faqs/can-you-predict-earthquakes>
- **ANSS Comprehensive Earthquake Catalog (ComCat)** — USGS documentation for the U.S.
  earthquake catalog — <https://earthquake.usgs.gov/data/comcat/>
- **Completeness magnitude in earthquake catalogs** — Mignan & Woessner (2012), CORSSA;
  estimating `Mc` before you fit Gutenberg–Richter — <https://www.corssa.org/en/articles/theme_4/>
- **ETAS** — Ogata (1988), *Statistical models for earthquake occurrences and residual
  analysis for point processes*, J. Am. Stat. Assoc. 83, 9–27; the classic
  aftershock-triggering model — <https://doi.org/10.1080/01621459.1988.10478560>
- **CSEP** — Collaboratory for the Study of Earthquake Predictability; how earthquake
  forecasts are tested — <https://cseptesting.org/>
- **Kp index** — GFZ; the index behind the `geomagnetic` stream — <https://kp.gfz.de/en/>
- **Probability calibration** — scikit-learn user guide; isotonic regression and
  reliability curves — <https://scikit-learn.org/stable/modules/calibration.html>
