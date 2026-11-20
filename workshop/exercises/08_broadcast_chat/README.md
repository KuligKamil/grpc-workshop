# Exercise 8 (bonus): A real chat — broadcasting

**Estimated time:** ~25 min

## Goal

Make `Chat` deliver each message to **everyone in the room**, not just back to
its sender.

## Why the current version isn't a chat

The `Chat` from Exercise 5 echoes:

```python
def Chat(self, request_iterator, context):
    for request in request_iterator:
        yield _make_message(request)
```

Each call only ever writes to the stream it is reading from, so two people in
`general` never see each other. Try it — open `poe final-chat` twice and type
in both. Everyone is talking to themselves.

## The idea

Separate *receiving* from *sending*:

- every connected stream gets its own **queue** (its inbox)
- the room keeps a list of the inboxes currently subscribed to it
- an incoming message is stored, then **put into every inbox for that room**
- the generator yields whatever lands in its own inbox

```
alice's Chat ──reads──> [store] ──fan out──> alice's queue ──yields──> alice
                                        └──> bob's queue   ──yields──> bob
```

## Things you have to get right

**1. Reading and writing happen at the same time.** `for request in
request_iterator` blocks until the next request arrives, so you cannot also sit
in a loop yielding replies. The reference solution reads on a separate thread
and lets the generator drain the queue.

**2. The server is multi-threaded.** gRPC serves each call on its own thread
from the pool, so the subscriber registry and the store need a `threading.Lock`.

**3. You must clean up, and `return` is not enough.** A client that disappears
(Ctrl-C, lost network, cancelled call) never finishes its request iterator. Use
the hook gRPC gives you:

```python
context.add_callback(_unsubscribe)
```

It runs however the call ends. Without it, every disconnect leaves a queue
registered and the server keeps fanning messages into a buffer nobody reads —
a slow leak that only shows up after a while.

**4. The room isn't known until the first message.** `Chat(stream)` carries no
room in the call itself, so subscription happens when the first request arrives.
(A more realistic API would put the room in metadata — see the metadata bonus.)

## Reference implementation

`server_broadcast.py` in this directory is a complete, working version. Read it
after you have tried, or run it directly:

```bash
poe server-broadcast
```

## Demo: two terminals

```bash
# Terminal 1
poe server-broadcast

# Terminal 2
poe final-chat --room general --user alice

# Terminal 3
poe final-chat --room general --user bob
```

Type in Alice's terminal and it appears in Bob's. Note that Bob only sees
messages sent *after* he joined — this is a live stream, not a backlog. Call
`poe final-history` to get what he missed.

## Verify

```bash
poe test-08
```

The tests drive two real gRPC streams and check that Alice sees Bob's message,
that messages do not leak between rooms, and that a disconnected client's queue
is actually unregistered.

## Going further

- Send the room backlog when someone joins (`GetHistory` + the live stream),
  and think about the message that arrives *between* the two.
- Use `context.is_active()` to drop a subscriber that has stopped reading.
- Replace the unbounded queue with `queue.Queue(maxsize=...)` and decide what a
  slow client should do: block the publisher, or lose messages?
