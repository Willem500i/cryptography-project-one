# Group chat simulation: who sends when, when messages are delivered to everyone.
# TODO for Gaurav

# --- Outline: implement below ---
# Idea: simulate m parties in a chat; when party i "sends", that corresponds to
# using the next pad(s) in the protocol. When a message "arrives" at all others,
# that corresponds to deliver_message so in_flight stays bounded by d.
#
# Possible interface (adjust to what you build):
#   - run_sim(n, m, d, L, ...) -> drives protocol.send_message / deliver_message
#     and returns final state + stats, so testing can call this instead of
#     run_execution for simulator-based runs.
#   - Or: produce a sequence of (sender_id, deliver_which?) that testing or
#     protocol uses to step the protocol.
# Add your functions below and update this comment with how to use them.


def step_send(sender_id: int):
    """Simulate one party sending a message to the group. Hook into protocol.send_message when ready."""
    ...


def step_deliver(msg):
    """Simulate a message being delivered to all recipients. Hook into protocol.deliver_message when ready."""
    ...


# Add more as needed (e.g. run_sim, or event loop that calls step_send / step_deliver).
