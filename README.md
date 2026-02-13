# Cryptography Project 1 — Multi-party one-time pad protocol

Outline for m-party async communication with perfect secrecy (m=3 or 4). Fill in the stubs in `protocol.py` and `testing.py`.

---

## Run the protocol (quick check)

From the project root:

```bash
python protocol.py
```

- Runs a single execution with defaults: m=3, n=100, d=5, L=1.
- Once implemented, it should print rounds completed and wasted pads.

---

## Run the testing program

From the project root:

```bash
python testing.py
```

- Runs scenarios **S.1** (one random sender), **S.2** (two random senders), **S.m** (all m parties).
- For each scenario: average wasted pads and average rounds over several trials.
- Execution ends when at least one active party can’t send securely (single pad sequence per run).

**Optional arguments:**

| Argument      | Meaning                          | Default        |
|---------------|----------------------------------|----------------|
| `-n`, `--pads`| Pad sequence length n            | 1000           |
| `-d`          | Max undelivered messages         | from protocol  |
| `-m`          | Number of parties                | from protocol  |
| `--trials`    | Trials per scenario              | 100            |
| `--seed`      | Random seed (reproducibility)     | 42             |

Example:

```bash
python testing.py -n 500 -d 5 --trials 200 --seed 123
```

---

## Files (what each one is for)

- **protocol.py** — Core protocol: pad allocation (`init_party_states`), secrecy condition (`undelivery_secrecy_condition`), send/deliver and one execution loop (`run_execution`). Implement the dataclass fields and all `...` bodies.
- **testing.py** — Test harness: pick active senders per scenario, run trials, report avg wasted pads and rounds. Implement so it calls `protocol.run_execution` and `protocol.count_wasted_pads`.
- **requirements.txt** — Python 3.8+; no extra packages required for the outline.
