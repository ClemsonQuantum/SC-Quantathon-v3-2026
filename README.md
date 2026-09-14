# SC Quantathon v3 2026

Bootcamp and challenge materials for SC Quantathon v3, the 24-hour quantum computing hackathon hosted by Clemson Quantum Club at the Watt Family Innovation Center, Clemson University, September 25–27, 2026.

SC Quantum founded the Quantathon and ran its first two editions in the Southeast. This third edition is hosted at Clemson. Teams of 3–5 undergraduate or graduate students, 18 or older, take on a challenge written by one of three challenge sponsors, build for 24 hours, and present to judges on Sunday.

## Links

| | |
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
| September 14–25 | Bootcamp, one entry per weekday |
| Friday, September 25, 5:00 PM | Check-in and welcome ceremony |
| Saturday, September 26, 10:00 AM | Hacking begins |
| Sunday, September 27, 10:00 AM | Submissions close on Devpost |
| Sunday, September 27, 12:00 PM | Judging presentations |
| Sunday, September 27, 6:00 PM | Awards ceremony |

## Bootcamp

The bootcamp is self-paced and released one weekday at a time from September 14 to 25. Each day has written notes and a notebook you can run; Day 2 is a recorded demo from qBraid. It assumes no prior quantum experience and is open to everyone, registered or not. Materials land in `bootcamp/` as they are posted.

| Day | Date | Topic |
|---|---|---|
| 1 | Mon, Sep 14 | Setup, Python Refresher, and Your First Circuit |
| 2 | Tue, Sep 15 | qBraid Platform Demo: Lab, Credits, and Submitting to a QPU (recorded, Alex Van Bussum, qBraid) |
| 3 | Wed, Sep 16 | The Math Behind a Qubit |
| 4 | Thu, Sep 17 | Single-Qubit Gates and Measurement |
| 5 | Fri, Sep 18 | Multi-Qubit Gates and Entanglement |
| 6 | Mon, Sep 21 | Real Hardware: Transpilation, Noise, and Error Mitigation |
| 7 | Tue, Sep 22 | Variational Algorithms: VQE, QAOA, and a Taste of QML |
| 8 | Wed, Sep 23 | SRNL: Mapping Applied Research to Qubits |
| 9 | Thu, Sep 24 | Quantum Rings: Simulating Beyond Statevector |
| 10 | Fri, Sep 25 | IonQ: Trapped Ions and Native Gates |

## Challenges

Three challenge sponsors each write one challenge. Teams rank their preferences Friday evening, assignments are posted Friday at 10:00 PM, and full briefs are released at the Saturday opening ceremony. Briefs and any starter material are added to `challenges/` at that point, not before.

- Savannah River National Laboratory
- Quantum Rings
- IonQ

## Repository layout

```
SC-Quantathon-v3/
  README.md
  LICENSE                      # Apache-2.0
  bootcamp/
    day-01/                    # notes.md, notebook.ipynb
    day-02/
    ...
    day-10/
  challenges/
    srnl/                      # Released Saturday, September 26 at the opening ceremony
    quantum-rings/
    ionq/
```

## Running the notebooks

The notebooks are written to run on [qBraid Lab](https://lab.qbraid.com/), the environment used during the hackathon. Create a free qBraid account at https://account.qbraid.com/ with the email you registered with; accepted participants are added to the SC Quantathon v3 organization on qBraid to receive credits, with no access key to enter. Also create an IBM Quantum account at https://quantum.cloud.ibm.com/ and save your API key. Those two are all you need in advance; the free IBM Open Plan gives up to 10 minutes of QPU time per 28 days, so debug on simulators first.

To run locally instead:

```bash
git clone https://github.com/ClemsonQuantum/SC-Quantathon-v3.git
cd SC-Quantathon-v3
conda create -n scqv3 python=3.12
conda activate scqv3
pip install -r requirements.txt
jupyter lab
```

A `requirements.txt` is added with the first notebook.

## Submissions

Every team submits once on Devpost before Sunday, September 27 at 10:00 AM. The Devpost rules page lists what to include and how to package the ZIP. All project code is written inside the hacking window; brainstorming beforehand is fine.

## Sponsors

Challenge sponsors: Savannah River National Laboratory, Quantum Rings, IonQ.
Powered by qBraid. Hosted by the Watt Family Innovation Center.
Partners: South Carolina Quantum, Clemson University College of Engineering, Computing and Applied Sciences, TraCR (National Center for Transportation Cybersecurity and Resiliency), Western Carolina University College of Engineering and Technology, GVL Limo, Robinson Bradshaw.

## License

Apache-2.0. See `LICENSE`.
