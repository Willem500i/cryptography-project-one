# m-party one-time pad. m=3 or 4, n pads, d max undelivered, L pads per message.
# Design: Between redistributions, each party uses only their local list of allowed pads (async).
# Every REDISTRIBUTE_EVERY messages they come together, agree on a new split of unused pads,
# each saves their new list locally, then continues async. Benefit: low waste without per-message coordination.

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# --- Parameters ---
M = 3
D = 5
L = 1
REDISTRIBUTE_EVERY = 20  # every this many messages, parties sync and redistribute unused pads


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
        for party in self.parties:
            if party.party_id != sender.party_id:
                party.receive(message, sender)


class Party:
    def __init__(self, party_id: int, channel: Channel, state: PartyState):
        self.party_id = party_id
        self.channel = channel
        self.state = state

    def send(self, ciphertext: InFlightMessage) -> None:
        self.channel.broadcast(ciphertext, self)

    def receive(self, ciphertext: InFlightMessage, sender: "Party") -> None:
        pass


# --- Allocation: each party uses their local list until next redistribution ---
def pads_for_message(party: Party, L: int) -> List[int]:
    if party.state.offset + L > len(party.state.indices):
        return []
    return party.state.indices[party.state.offset : party.state.offset + L]


def redistribute(channel: Channel) -> None:
    """Parties come together and agree on a new split of unused pads; each saves their new list locally."""
    free = [i for i in range(channel.n) if channel.pad_owner[i] is None]
    if not free:
        return
    m = channel.m
    size = len(free)
    chunk_size = size // m
    remainder = size % m
    start = 0
    for j in range(m):
        take = chunk_size + (1 if j < remainder else 0)
        channel.parties[j].state.indices = free[start : start + take]
        channel.parties[j].state.offset = 0
        start += take


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
    party.send(msg)
    return msg


# --- Delivery ---
def deliver_message(channel: Channel, msg: InFlightMessage) -> None:
    channel.in_flight.remove(msg)


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
) -> Tuple[Channel, int, int]:
    channel = Channel(m, n, d, L)
    rng = rng or random.Random()
    active_parties = [channel.parties[i] for i in active_senders]
    rounds = 0
    messages_since_redist = 0
    num_redistributions = 0
    while True:
        sender = rng.choice(active_parties)
        if not can_send(channel, sender):
            break
        send_message(channel, sender)
        rounds += 1
        messages_since_redist += 1
        if messages_since_redist >= REDISTRIBUTE_EVERY:
            redistribute(channel)
            messages_since_redist = 0
            num_redistributions += 1
        while len(channel.in_flight) > d:
            step_deliveries(channel, 1)
        if max_rounds is not None and rounds >= max_rounds:
            break
    return channel, rounds, num_redistributions


# --- Main ---
if __name__ == "__main__":
    channel, rounds, num_redist = run_execution(100, M, D, L, list(range(M)))
    print("rounds", rounds, "wasted", count_wasted_pads(channel), "redistributions", num_redist)
