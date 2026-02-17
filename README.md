# Cryptography Project 1 — Multi-party one-time pad protocol

m-party asynchronous communication with perfect secrecy (no pad reused). Supports m=3, 4, or more; uses periodic redistribution so parties work asynchronously between sync points and waste few pads.

---

## How the protocol works

- **Shared pad sequence:** There is one pad sequence of length **n** (indices 0..n-1). Each message uses **L** pad(s) (L=1 in the assignment).
- **Parties:** **m** parties (e.g. 3 or 4). Each has a **local list** of pad indices they are allowed to use and an **offset** into that list. They use pads only from this list, in order—no per-message coordination with others (async between syncs).
- **Start:** Pads are split into m equal segments; party i gets segment i (e.g. party 0 gets 0..n/m-1, etc.). Each party stores their segment as their local list.
- **Send:** When a party sends, it uses the next L pad(s) from its local list, marks those pads as used, and adds the message to **in_flight**. No central “who used what” check is needed for the send decision—the list is disjoint from others’ lists until the next redistribution.
- **Delivery:** The network can have at most **d** undelivered messages. When in_flight would exceed d, we **deliver** one message (remove it from in_flight). On delivery, every other party’s **receive()** is called (chat sim: “message delivered to all m-1 others”).
- **Redistribution:** Every **REDISTRIBUTE_EVERY** messages, parties run a **sync phase** so the new split uses only information they could have in a distributed setting: (1) **Drain in-flight** (deliver all pending messages). (2) Each party’s “used” pads are derived from its **local state** (indices[0:offset]). (3) The **free** set is computed as all indices minus the union of those reported-used sets (no global `pad_owner` is used for this decision). (4) Free is split evenly into m new lists and each party gets a new list and offset=0. They then continue asynchronously. `pad_owner` is kept only for bookkeeping and correctness checks, not for protocol decisions.
- **Stop:** The run ends when at least one active party cannot send (its local list doesn’t have L pads left). **Wasted pads** = number of pad indices never used.

Parameters (in `protocol.py`): **M** (parties), **D** (max undelivered), **L** (pads per message), **REDISTRIBUTE_EVERY**.

---

## Run the protocol (dummy demo)

From the project root:

```bash
python protocol.py
```

This runs a **dummy demo** that shows the protocol step-by-step:

- **Setup:** n=600, m=3, d=5, L=1, redistribute every 50 messages (see REDISTRIBUTE_EVERY in protocol). Run continues until no party can send (no artificial round limit).
- **Verbose output:** The **first 10 rounds** are printed in full: each round shows which party sends (and which pads), when in_flight exceeds d (and one message is delivered), and when a redistribution happens (sync + new list lengths). After that, one line says that later rounds are omitted and the run continues to completion.
- **End:** Prints “Stop: no party can send …” and a **Done** line with total rounds, wasted pads (as count and % of n), number of redistributions, and chat sim deliveries. This demonstrates that waste is a small fraction of n (e.g. a few percent) when the protocol runs to completion.

So the demo both illustrates the steps (send → in_flight → delivery when > d → redistribution every K messages) and shows the algorithm’s efficiency (low wasted %).

---

## Run the testing suite

From the project root:

```bash
python testing.py
```

**What it does:** Runs three **scenarios** (S.1, S.2, S.m) for one value of m. In each scenario, **x** is the number of parties that are allowed to send; who sends the next message is chosen at random among those x parties. Each run uses a single pad sequence and ends when at least one of the x parties cannot send securely.

- **S.1 (x=1):** Only one randomly chosen party sends (all others idle).
- **S.2 (x=2):** Two randomly chosen parties send (taking turns at random).
- **S.m (x=m):** All m parties can send (random interleaving).

For each scenario the script runs many **trials** and reports:

- **Avg wasted pads** and **wasted %** of n  
- **Avg rounds** (messages sent before stop)  
- **Time** (wall clock for that scenario)  
- **Async efficiency:** avg number of redistributions and avg messages per redistribution (higher = more async)  
- **Chat sim:** avg number of deliveries (receive calls) per run  

**Arguments:**

| Argument       | Meaning                              | Default        |
|----------------|--------------------------------------|----------------|
| `-n`, `--pads` | Pad sequence length n                | from m (see below) |
| `-d`           | Max undelivered messages             | from m or protocol |
| `-m`           | Number of parties                    | from protocol (M=3) |
| `--trials`     | Trials per scenario                  | 100            |
| `--seed`       | Random seed                          | 42             |
| `--sweep-m`    | Run m = 3, 4, 5, 10, 100 with scaled n, d | off    |

When you don’t pass `-n`, n and d are chosen from m: for m≤4 use n=1000, d=5; for m>4 use n=500×m and d = max(5, min(100, n/100)).

**Examples:**

```bash
python testing.py
python testing.py -m 4 -n 1000 --trials 50
python testing.py --sweep-m --trials 10
```

With **--sweep-m**, the script runs the same three scenario types for m = 3, 4, 5, 10, and 100 (with scaled n and d for each m), and prints total time per m.

---

## Files

- **protocol.py** — Protocol and chat sim: `Channel`, `Party`, pad allocation (local lists), send/deliver, redistribution, `run_execution`, wasted-pad count. Contains the dummy demo in `if __name__ == "__main__"`.
- **testing.py** — Test harness: scenarios S.1, S.2, S.m; calls `run_execution` and reports waste %, rounds, time, async efficiency, and chat sim deliveries. Supports single-m and `--sweep-m`.
- **requirements.txt** — Python 3.8+; no extra packages required.
