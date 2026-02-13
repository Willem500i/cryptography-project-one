# m-party one-time pad. m=3 or 4, n pads, d max undelivered, L pads per message.

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# --- Parameters ---
M = 3
D = 5
L = 1

# --- Data structures ---
@dataclass
class InFlightMessage:
    # sent but not yet delivered; need to know sender and which pads so we can enforce d
    pass


@dataclass
class PartyState:
    # e.g. party_id, next pad index to use, direction (+1 or -1) or segment
    pass


@dataclass
class ProtocolState:
    # n, m, d, L; list of PartyState; pad_owner[i] = who used pad i (or None); in_flight list
    pass

# --- Allocation ---
def init_party_states(m: int, n: int) -> List[PartyState]:
    # set starting index and direction for each party so pads don't overlap (think 2-party: one from 0, one from n-1)
    ...


def pads_for_message(party: PartyState, L: int) -> List[int]:
    # the L indices this party would use for its next message
    ...

# --- Secrecy and send ---
def undelivery_secrecy_condition(state: ProtocolState, party_id: int, pad_indices: List[int]) -> bool:
    # true iff using these pads is safe: no double use, and with up to d undelivered no other party could be using them
    ...


def can_send(state: ProtocolState, party_id: int) -> bool:
    # pads in range and undelivery_secrecy_condition holds
    ...


def send_message(state: ProtocolState, party_id: int) -> Optional[InFlightMessage]:
    # if can_send: mark pads used, advance party's index, add to in_flight, return message. else None
    ...

# --- Delivery ---
def deliver_message(state: ProtocolState, msg: InFlightMessage) -> None:
    # remove from in_flight (simulate "everyone got it")
    ...


def step_deliveries(state: ProtocolState, max_deliver: int = 1) -> None:
    # call deliver_message on up to max_deliver in-flight msgs (keeps |in_flight| <= d in run_execution)
    ...

# --- Execution and stats ---
def count_wasted_pads(state: ProtocolState) -> int:
    # how many pads in [0..n-1] were never used
    ...


def run_execution(n: int, m: int, d: int, L: int, active_senders: List[int],
                  rng: Optional[random.Random] = None, max_rounds: Optional[int] = None) -> Tuple[ProtocolState, int]:
    # loop: pick random active sender; if can_send then send_message, maybe step_deliveries to cap in_flight at d; else stop. return (state, rounds)
    ...

# --- Main ---
if __name__ == "__main__":
    # run_execution(...), then print rounds and count_wasted_pads(state)
    ...
