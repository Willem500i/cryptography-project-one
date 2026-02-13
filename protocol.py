# m-party one-time pad. m=3 or 4, n pads, d max undelivered, L pads per message.

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# --- Parameters ---
M = 3
D = 5
L = 1
REDISTRIBUTE_EVERY = 20  # re-split unused pads among parties every this many messages

# --- Data structures ---
@dataclass
class InFlightMessage:
    sender_id: int
    pad_indices: List[int]


@dataclass
class PartyState:
    party_id: int
    indices: List[int]   # pad indices this party may use (order they'll use them)
    offset: int          # next index to use is indices[offset]


@dataclass
class ProtocolState:
    n: int
    m: int
    d: int
    L: int
    parties: List[PartyState]
    pad_owner: List[Optional[int]]
    in_flight: List[InFlightMessage]

# --- Allocation ---
# Start with equal segments; redistribute() re-splits unused pads so heavy senders can use more.
def init_party_states(m: int, n: int) -> List[PartyState]:
    chunk = n // m
    out = []
    for i in range(m):
        start = i * chunk
        end = (i + 1) * chunk if i < m - 1 else n
        out.append(PartyState(party_id=i, indices=list(range(start, end)), offset=0))
    return out


def pads_for_message(party: PartyState, L: int) -> List[int]:
    if party.offset + L > len(party.indices):
        return []
    return party.indices[party.offset : party.offset + L]


def redistribute(state: ProtocolState) -> None:
    """Take all unused pads, split evenly among m parties. Call every REDISTRIBUTE_EVERY messages."""
    free = [i for i in range(state.n) if state.pad_owner[i] is None]
    if not free:
        return
    # split into m roughly equal parts
    m = state.m
    size = len(free)
    chunk_size = size // m
    remainder = size % m
    start = 0
    for j in range(m):
        take = chunk_size + (1 if j < remainder else 0)
        state.parties[j].indices = free[start : start + take]
        state.parties[j].offset = 0
        start += take

# --- Secrecy and send ---
def undelivery_secrecy_condition(state: ProtocolState, party_id: int, pad_indices: List[int]) -> bool:
    for i in pad_indices:
        if state.pad_owner[i] is not None:
            return False
    return True


def can_send(state: ProtocolState, party_id: int) -> bool:
    party = state.parties[party_id]
    indices = pads_for_message(party, state.L)
    if len(indices) != state.L:
        return False
    return undelivery_secrecy_condition(state, party_id, indices)


def send_message(state: ProtocolState, party_id: int) -> Optional[InFlightMessage]:
    if not can_send(state, party_id):
        return None
    party = state.parties[party_id]
    indices = pads_for_message(party, state.L)
    for i in indices:
        state.pad_owner[i] = party_id
    msg = InFlightMessage(sender_id=party_id, pad_indices=indices.copy())
    party.offset += state.L
    state.in_flight.append(msg)
    return msg

# --- Delivery ---
def deliver_message(state: ProtocolState, msg: InFlightMessage) -> None:
    state.in_flight.remove(msg)


def step_deliveries(state: ProtocolState, max_deliver: int = 1) -> None:
    for _ in range(min(max_deliver, len(state.in_flight))):
        if state.in_flight:
            deliver_message(state, state.in_flight[0])

# --- Execution and stats ---
def count_wasted_pads(state: ProtocolState) -> int:
    return sum(1 for o in state.pad_owner if o is None)


def run_execution(n: int, m: int, d: int, L: int, active_senders: List[int],
                  rng: Optional[random.Random] = None, max_rounds: Optional[int] = None) -> Tuple[ProtocolState, int]:
    rng = rng or random.Random()
    pad_owner = [None] * n
    parties = init_party_states(m, n)
    state = ProtocolState(n=n, m=m, d=d, L=L, parties=parties, pad_owner=pad_owner, in_flight=[])
    rounds = 0
    messages_since_redist = 0
    while True:
        sender = rng.choice(active_senders)
        if not can_send(state, sender):
            break
        send_message(state, sender)
        rounds += 1
        messages_since_redist += 1
        if messages_since_redist >= REDISTRIBUTE_EVERY:
            redistribute(state)
            messages_since_redist = 0
        while len(state.in_flight) > d:
            step_deliveries(state, 1)
        if max_rounds is not None and rounds >= max_rounds:
            break
    return state, rounds

# --- Main ---
if __name__ == "__main__":
    state, rounds = run_execution(100, M, D, L, list(range(M)))
    print("rounds", rounds, "wasted", count_wasted_pads(state))
