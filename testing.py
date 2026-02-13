# Test protocol: S.1 (1 sender), S.2 (2 senders), S.m (all). Avg wasted pads over trials.

import argparse
import random
from typing import List, Tuple

from protocol import M, D, L, run_execution, count_wasted_pads


def scenario_active_senders(m: int, x: int, rng: random.Random) -> List[int]:
    return rng.sample(range(m), min(x, m))


def run_one_trial(n: int, m: int, d: int, L: int, active_senders: List[int], rng: random.Random) -> Tuple[int, int]:
    state, rounds = run_execution(n, m, d, L, active_senders, rng=rng)
    return count_wasted_pads(state), rounds


def run_scenario(scenario_name: str, n: int, m: int, d: int, L: int, x: int, num_trials: int, base_seed: int) -> None:
    wasted_list, rounds_list = [], []
    for t in range(num_trials):
        rng = random.Random(base_seed + t)
        active = scenario_active_senders(m, x, rng)
        w, r = run_one_trial(n, m, d, L, active, rng)
        wasted_list.append(w)
        rounds_list.append(r)
    avg_w = sum(wasted_list) / len(wasted_list)
    avg_r = sum(rounds_list) / len(rounds_list)
    print(f"  {scenario_name}: avg wasted = {avg_w:.1f}, avg rounds = {avg_r:.1f}")


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
