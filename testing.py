# Test protocol: S.1 (1 sender), S.2 (2 senders), S.m (all). Avg wasted pads over trials.

import argparse
import random
import time
from typing import List, Tuple

from protocol import M, D, L, run_execution, count_wasted_pads


def scenario_active_senders(m: int, x: int, rng: random.Random) -> List[int]:
    return rng.sample(range(m), min(x, m))


def run_one_trial(n: int, m: int, d: int, L: int, active_senders: List[int], rng: random.Random) -> Tuple[int, int, int]:
    channel, rounds, num_redist = run_execution(n, m, d, L, active_senders, rng=rng)
    return count_wasted_pads(channel), rounds, num_redist


def run_scenario(scenario_name: str, n: int, m: int, d: int, L: int, x: int, num_trials: int, base_seed: int) -> float:
    wasted_list, rounds_list, redist_list = [], [], []
    t0 = time.perf_counter()
    for t in range(num_trials):
        rng = random.Random(base_seed + t)
        active = scenario_active_senders(m, x, rng)
        w, r, rd = run_one_trial(n, m, d, L, active, rng)
        wasted_list.append(w)
        rounds_list.append(r)
        redist_list.append(rd)
    elapsed = time.perf_counter() - t0
    avg_w = sum(wasted_list) / len(wasted_list)
    avg_r = sum(rounds_list) / len(rounds_list)
    avg_redist = sum(redist_list) / len(redist_list)
    pct = 100 * avg_w / n if n else 0
    msgs_per_redist = avg_r / avg_redist if avg_redist > 0 else float("inf")
    print(f"  {scenario_name}: avg wasted = {avg_w:.1f} ({pct:.2f}%), avg rounds = {avg_r:.1f}, time = {elapsed:.2f}s")
    print(f"    async efficiency: avg redistributions = {avg_redist:.1f}, avg messages per redistribution = {msgs_per_redist:.1f}")
    return elapsed


def default_n_d_for_m(m: int) -> Tuple[int, int]:
    """Scale n and d for larger m so there are enough pads and in-flight headroom."""
    if m <= 4:
        return 1000, 5
    n = 500 * m
    d = max(5, min(100, n // 100))
    return n, d


def main():
    parser = argparse.ArgumentParser(description="Test m-party pad protocol (avg wasted pads per scenario)")
    parser.add_argument("-n", "--pads", type=int, default=None, help="pad sequence length n (default: from m)")
    parser.add_argument("-d", type=int, default=None, help="max undelivered (default: from m or protocol)")
    parser.add_argument("-m", type=int, default=None, help="number of parties (default: from protocol)")
    parser.add_argument("--trials", type=int, default=100, help="trials per scenario")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--sweep-m", action="store_true", help="run m in 3,4,5,10,100 with scaled n,d")
    args = parser.parse_args()

    if args.sweep_m:
        for m in (3, 4, 5, 10, 100):
            n, d = default_n_d_for_m(m)
            print(f"\n--- m={m}, n={n}, d={d}, L={L}, trials={args.trials} ---")
            t1 = time.perf_counter()
            run_scenario("S.1 (x=1)", n, m, d, L, x=1, num_trials=args.trials, base_seed=args.seed)
            run_scenario("S.2 (x=2)", n, m, d, L, x=2, num_trials=args.trials, base_seed=args.seed)
            run_scenario(f"S.{m} (x={m})", n, m, d, L, x=m, num_trials=args.trials, base_seed=args.seed)
            total = time.perf_counter() - t1
            print(f"  (m={m} total: {total:.2f}s)")
        print("\ndone")
        return

    m = args.m if args.m is not None else M
    if args.pads is not None:
        n = args.pads
        d = args.d if args.d is not None else D
    else:
        n, d = default_n_d_for_m(m)
        if args.d is not None:
            d = args.d

    print(f"m={m}, n={n}, d={d}, L={L}, trials={args.trials}, seed={args.seed}")
    t0 = time.perf_counter()
    run_scenario("S.1 (x=1)", n, m, d, L, x=1, num_trials=args.trials, base_seed=args.seed)
    run_scenario("S.2 (x=2)", n, m, d, L, x=2, num_trials=args.trials, base_seed=args.seed)
    run_scenario(f"S.{m} (x={m})", n, m, d, L, x=m, num_trials=args.trials, base_seed=args.seed)
    print(f"total time: {time.perf_counter() - t0:.2f}s")
    print("done")


if __name__ == "__main__":
    main()
