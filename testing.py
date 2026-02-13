# Test protocol: S.1 (1 sender), S.2 (2 senders), S.m (all). Avg wasted pads over trials.

import argparse
import random
from typing import List, Tuple

from protocol import M, D, L, run_execution, count_wasted_pads


def scenario_active_senders(m: int, x: int, rng: random.Random) -> List[int]:
    # which x parties can send this run (random subset of 0..m-1)
    ...


def run_one_trial(n: int, m: int, d: int, L: int, active_senders: List[int], rng: random.Random) -> Tuple[int, int]:
    # run_execution with these active_senders; return (wasted_pads, rounds)
    ...


def run_scenario(scenario_name: str, n: int, m: int, d: int, L: int, x: int, num_trials: int, base_seed: int) -> None:
    # for each trial get active_senders via scenario_active_senders(m, x, rng), run_one_trial, collect (wasted, rounds); print scenario_name and averages
    ...


def main():
    parser = argparse.ArgumentParser(description="Test m-party pad protocol (avg wasted pads per scenario)")
    parser.add_argument("-n", "--pads", type=int, default=1000, help="pad sequence length n")
    parser.add_argument("-d", type=int, default=None, help="max undelivered (default: from protocol)")
    parser.add_argument("-m", type=int, default=None, help="number of parties (default: from protocol)")
    parser.add_argument("--trials", type=int, default=100, help="trials per scenario")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    args = parser.parse_args()

    n = args.pads
    d = args.d if args.d is not None else D
    m = args.m if args.m is not None else M

    print(f"m={m}, n={n}, d={d}, L={L}, trials={args.trials}, seed={args.seed}")
    run_scenario("S.1 (x=1)", n, m, d, L, x=1, num_trials=args.trials, base_seed=args.seed)
    run_scenario("S.2 (x=2)", n, m, d, L, x=2, num_trials=args.trials, base_seed=args.seed)
    run_scenario(f"S.{m} (x={m})", n, m, d, L, x=m, num_trials=args.trials, base_seed=args.seed)
    print("done")


if __name__ == "__main__":
    main()
