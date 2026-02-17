# m-party one-time pad. m=3 or 4, n pads, d max undelivered, L pads per message.
# Design: Between redistributions, each party uses only their local list of allowed pads (async).
# Every REDISTRIBUTE_EVERY messages they come together, agree on a new split of unused pads,
# each saves their new list locally, then continues async. Benefit: low waste without per-message coordination.

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# --- Parameters ---
M = 3
D = 12
L = 1
REDISTRIBUTE_EVERY = 50  # every this many messages, parties sync and redistribute unused pads (larger = more async, fewer sync points)


# --- Data structures ---
@dataclass
class InFlightMessage:
    sender_id: int
    pad_indices: List[int]


@dataclass
class PartyState:
    indices: List[int]  # pad indices this party may use (saved locally after each redistribution)
    offset: int         # next index to use is indices[offset]


# Chat simulation (Channel/Party) + protocol
class Channel:
    def __init__(self, m: int, n: int, d: int, l: int):
        self.n = n
        self.m = m
        self.d = d
        self.L = l
        self.pad_owner = [None] * n
        self.in_flight: List[InFlightMessage] = []
        self.parties: List["Party"] = []
        self.deliveries_count = 0  # number of receive() calls (chat sim: message delivered to a party)
        self.verbose = False
        # initial equal segments; each party saves their list locally
        self._init_party_states(m, n)

    def _init_party_states(self, m: int, n: int) -> None:
        chunk = n // m
        for i in range(m):
            start = i * chunk
            end = (i + 1) * chunk if i < m - 1 else n
            state = PartyState(indices=list(range(start, end)), offset=0)
            party = Party(party_id=i, channel=self, state=state)
            self.parties.append(party)

    def register_user(self, party: "Party") -> None:
        self.parties.append(party)

    def broadcast(self, message: InFlightMessage, sender: "Party") -> None:
        # Optional: use for "on send" notification. Protocol calls receive() on delivery (in deliver_message).
        for party in self.parties:
            if party.party_id != sender.party_id:
                party.receive(message, sender)


class Party:
    def __init__(self, party_id: int, channel: Channel, state: PartyState):
        self.party_id = party_id
        self.channel = channel
        self.state = state

    def send(self, ciphertext: InFlightMessage) -> None:
        # Optional: call from send_message for "on send" sim. Delivery sim uses deliver_message -> receive().
        self.channel.broadcast(ciphertext, self)

    def receive(self, ciphertext: InFlightMessage, sender: "Party") -> None:
        # Chat sim: this party has "received" the message (same-time delivery to all m-1 others).
        self.channel.deliveries_count += 1


# --- Allocation: each party uses their local list until next redistribution ---
def pads_for_message(party: Party, L: int) -> List[int]:
    if party.state.offset + L > len(party.state.indices):
        return []
    return party.state.indices[party.state.offset : party.state.offset + L]


def redistribute(channel: Channel) -> None:
    """Sync phase: drain in-flight, then compute free set from each party's reported state (not global pad_owner).
    All parties could do this in a distributed setting after exchanging their (indices, offset) and draining in-flight."""
    while channel.in_flight:
        deliver_message(channel, channel.in_flight[0])
    used_set = set()
    for p in channel.parties:
        used_set.update(p.state.indices[: p.state.offset])
    free = [i for i in range(channel.n) if i not in used_set]
    if not free:
        return
    m = channel.m
    size = len(free)
    chunk_size = size // m
    remainder = size % m
    start = 0
    lengths = []
    for j in range(m):
        take = chunk_size + (1 if j < remainder else 0)
        channel.parties[j].state.indices = free[start : start + take]
        channel.parties[j].state.offset = 0
        lengths.append(take)
        start += take
    if channel.verbose:
        print(f"  Redistribution: {size} unused pads split among {m} parties -> list lengths {lengths}")


# --- Secrecy: between redistributions lists are disjoint, so using from our list is safe ---
def undelivery_secrecy_condition(channel: Channel, party_id: int, pad_indices: List[int]) -> bool:
    for i in pad_indices:
        if channel.pad_owner[i] is not None:
            return False
    return True


def can_send(channel: Channel, party: Party) -> bool:
    indices = pads_for_message(party, channel.L)
    if len(indices) != channel.L:
        return False
    return undelivery_secrecy_condition(channel, party.party_id, indices)


def send_message(channel: Channel, party: Party) -> Optional[InFlightMessage]:
    if not can_send(channel, party):
        return None
    indices = pads_for_message(party, channel.L)
    for i in indices:
        channel.pad_owner[i] = party.party_id
    msg = InFlightMessage(sender_id=party.party_id, pad_indices=indices.copy())
    party.state.offset += channel.L
    channel.in_flight.append(msg)
    if channel.verbose:
        others = [p.party_id for p in channel.parties if p.party_id != party.party_id]
        print(f"  Party {party.party_id} sends (pads {indices}) -> in_flight now {len(channel.in_flight)} (will deliver to Parties {others} when delivered)")
    return msg


# --- Delivery ---
def deliver_message(channel: Channel, msg: InFlightMessage) -> None:
    sender = channel.parties[msg.sender_id]
    recipients = [p.party_id for p in channel.parties if p.party_id != msg.sender_id]
    for p in channel.parties:
        if p.party_id != msg.sender_id:
            p.receive(msg, sender)
    channel.in_flight.remove(msg)
    if channel.verbose:
        print(f"  Delivered: Party {msg.sender_id} -> Parties {recipients} (pads {msg.pad_indices})")


def step_deliveries(channel: Channel, max_deliver: int = 1) -> None:
    for _ in range(min(max_deliver, len(channel.in_flight))):
        if channel.in_flight:
            deliver_message(channel, channel.in_flight[0])


# --- Execution and stats ---
def count_wasted_pads(channel: Channel) -> int:
    return sum(1 for o in channel.pad_owner if o is None)


def run_execution(
    n: int,
    m: int,
    d: int,
    L: int,
    active_senders: List[int],
    rng: Optional[random.Random] = None,
    max_rounds: Optional[int] = None,
    verbose: bool = False,
    redistribute_every: Optional[int] = None,
    max_verbose_rounds: Optional[int] = None,
) -> Tuple[Channel, int, int]:
    every = redistribute_every if redistribute_every is not None else REDISTRIBUTE_EVERY
    channel = Channel(m, n, d, L)
    channel.verbose = verbose
    rng = rng or random.Random()
    active_parties = [channel.parties[i] for i in active_senders]
    rounds = 0
    messages_since_redist = 0
    num_redistributions = 0
    omitted_printed = False
    if verbose:
        print("Start: each party has local list of pad indices (equal segments).")
    while True:
        sender = rng.choice(active_parties)
        if not can_send(channel, sender):
            if verbose:
                print("Stop: no party can send (local list exhausted or pad conflict).")
            break
        if max_verbose_rounds is not None and rounds >= max_verbose_rounds and verbose and not omitted_printed:
            channel.verbose = False
            omitted_printed = True
            print(f"  ... rounds {max_verbose_rounds + 1} onward omitted (run continues to completion) ...")
        if channel.verbose:
            print(f"Round {rounds + 1}:")
        send_message(channel, sender)
        rounds += 1
        messages_since_redist += 1
        if messages_since_redist >= every:
            if verbose:
                print("  Sync: parties agree on new split of unused pads.")
            redistribute(channel)
            messages_since_redist = 0
            num_redistributions += 1
        while len(channel.in_flight) > d:
            if verbose:
                print(f"  (in_flight={len(channel.in_flight)} > d={d} -> deliver one)")
            step_deliveries(channel, 1)
        if max_rounds is not None and rounds >= max_rounds:
            break
    return channel, rounds, num_redistributions


# --- Main ---
if __name__ == "__main__":
    # Demo: real-sized run to show low waste; first 10 rounds printed in full, then run to completion
    demo_n, demo_m, demo_d = 600, 3, 5
    print(f"Demo: n={demo_n}, m={demo_m}, d={demo_d}, L={L}, redistribute every {REDISTRIBUTE_EVERY} messages")
    print("(First 10 rounds in full, then run to completion.)\n")
    channel, rounds, num_redist = run_execution(
        demo_n, demo_m, demo_d, L, list(range(demo_m)),
        rng=random.Random(42), verbose=True, max_verbose_rounds=10
    )
    wasted = count_wasted_pads(channel)
    pct = 100 * wasted / demo_n
    print(f"\nDone: rounds={rounds}, wasted={wasted}/{demo_n} ({pct:.1f}%), redistributions={num_redist}, chat sim deliveries={channel.deliveries_count}")
