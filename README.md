# SC Quantathon v3 2026

Bootcamp and challenge materials for SC Quantathon v3, the 24-hour quantum computing hackathon hosted by Clemson Quantum Club at the Watt Family Innovation Center, Clemson University, September 25–27, 2026.

SC Quantum founded the Quantathon and ran its first two editions in the Southeast. This third edition is hosted at Clemson. Teams of 3–5 undergraduate or graduate students take on a challenge written by one of two challenge sponsors, build for 24 hours, and present to judges on Sunday.

## Links

| What | Link |
|---|---|
| Event page, travel, hotels, FAQ | https://clemsonquantum.com/events/hackathons/sc-quantathon-v3-2026/ |
| Devpost (rules, submission, schedule) | https://sc-quantathon-v3.devpost.com/ |
| Registration | https://forms.gle/vWRNfTQMNQBrGFUh7 |
| Bootcamp page | https://clemsonquantum.com/events/workshops-and-seminars/sc-quantathon-v3-bootcamp-2026/ |
| Code of conduct | https://clemsonquantum.com/code-of-conduct/ |
| Contact | cqc@clemson.edu |

The Discord invite is sent to accepted participants by email.

## Key dates

| When | What |
|---|---|
| September 14–22 | Seven-day, self-paced bootcamp |
| Friday, September 25, 5:00 PM | Check-in |
| Friday, September 25, 5:30 PM | Welcome ceremony and challenge teasers |
| Saturday, September 26, 10:00 AM | Hacking begins |
| Sunday, September 27, 10:00 AM | Submissions close on Devpost |
| Sunday, September 27, 12:00 PM | Judging presentations |
| Sunday, September 27, 6:00 PM | Awards ceremony |

## Bootcamp

Seven-day, self-paced bootcamp, September 14–22, 2026. The schedule below lists all seven days. Each day has written notes and a notebook you can run; Day 3 is a recorded demo from qBraid. It assumes no prior quantum experience and is open to everyone, registered or not. Materials land in `bootcamp/` as they are posted, one folder per day with a notebook, a solutions notebook, and a PDF of notes. Day 3 is the exception: its folder holds the recording instead.

| Day | Date | Topic |
|---|---|---|
| 1 | Mon, Sep 14 | Setup, Python Refresher, and Your First Circuit |
| 2 | Tue, Sep 15 | The Math Behind a Qubit |
| 3 | Wed, Sep 16 | qBraid Platform Demo: Lab, Credits, and Submitting to a QPU (recorded, Alex Van Bussum, qBraid) |
| 4 | Thu, Sep 17 | Gates, Measurement, and Entanglement |
| 5 | Fri, Sep 18 | Real Hardware: Transpilation, Noise, and Error Mitigation |
| 6 | Mon, Sep 21 | Variational Algorithms: VQE and QAOA |
| 7 | Tue, Sep 22 | Quantum Machine Learning |

## Challenges

Two challenge sponsors each write one challenge. Teams rank their preferences Friday evening, assignments are posted Friday at 10:00 PM, and full briefs are released at the Saturday opening ceremony. Each challenge folder holds a README now; teasers are added Friday, September 25, and briefs plus any starter material at the opening ceremony on Saturday, September 26.

- Savannah River National Laboratory
- Quantum Rings

## Repository layout

```
SC-Quantathon-v3-2026/
  README.md
  LICENSE                      # Apache-2.0
  requirements.txt
  bootcamp/
    day-1/
      1, notebook - Setup, Python Refresher, and Your First Circuit.ipynb
      1, solutions - Setup, Python Refresher, and Your First Circuit.ipynb
      1, notes - Setup, Python Refresher, and Your First Circuit.pdf
      src/                     # LaTeX source and figure script for the notes
    day-2/                     # same three files plus src/
    day-3/                     # the recorded qBraid demo and a README; no notebook or notes
                               # days 4–7 follow the same structure as day 2
  challenges/
    srnl/                      # README now; brief and starter material Saturday, September 26
    quantum-rings/
```

Each bootcamp day has a notebook with exercises to complete, a solutions notebook with every exercise filled in and its outputs, and a PDF of notes that explains the same material with figures and references. Day 3 is a recorded demo from qBraid, so that folder holds the video and a README instead. All seven days are available.

## Running the notebooks

The notebooks are written to run on qBraid Lab, the environment used during the hackathon. Create a free qBraid account at https://account.qbraid.com/ with the email you registered with, and launch Lab from that dashboard by choosing a compute profile and clicking Launch; accepted participants are added to the SC Quantathon v3 organization on qBraid to receive credits, with no access key to enter. Also create an IBM Quantum account at https://quantum.cloud.ibm.com/ and create an API key and an Open Plan instance. The Day 1 notebook asks for the key and the instance CRN in a hidden prompt and saves them on disk; never paste either into a notebook cell. Those two are all you need in advance; the free IBM Open Plan gives up to 10 minutes of QPU time per 28 days, so debug on simulators first.

To run locally instead:

```bash
git clone https://github.com/ClemsonQuantum/SC-Quantathon-v3-2026.git
cd SC-Quantathon-v3-2026
conda create -n scqv3 python=3.12
conda activate scqv3
pip install -r requirements.txt
jupyter lab
```

The pinned `requirements.txt` is at the repository root; the notebooks are verified against it.

## Submissions

Every team submits once on Devpost before Sunday, September 27 at 10:00 AM. The Devpost rules page lists what to include and how to package the ZIP. All project code is written inside the hacking window; brainstorming beforehand is fine.

## Sponsors

Challenge sponsors: Savannah River National Laboratory and Quantum Rings.
Powered by qBraid. Hosted by the Watt Family Innovation Center.
Partners: South Carolina Quantum, Clemson University College of Engineering, Computing and Applied Sciences, TraCR (National Center for Transportation Cybersecurity and Resiliency), Western Carolina University College of Engineering and Technology, GVL Limo, Robinson Bradshaw.

## License

Apache-2.0. See `LICENSE`.
