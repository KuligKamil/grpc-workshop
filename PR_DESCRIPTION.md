Large additions from section D of the review, kept out of `review-fixes` so they can be reviewed on their own. Base is `review-fixes`, so this diff is only the three new bonuses.

## What's here

**#17 — Exercise 8: a real chat (broadcast)** — `exercises/08_broadcast_chat/`

Until now `Chat` echoed each message back to its sender, so two clients in the same room never saw each other: the "final chat" was everyone talking to themselves. The reference server gives every stream its own queue, fans each message out to the room, and unregisters on disconnect via `context.add_callback`.

The README covers the three things that make this non-trivial: reading and writing concurrently (a reader thread), the lock a multi-threaded gRPC server needs, and cleanup for clients that never finish their request iterator.

Adds `poe server-broadcast` and `poe test-08`. The tests drive two real gRPC streams and assert that Alice sees Bob's message, that rooms stay isolated, and that a dropped client's queue is actually removed. Verified live with two participants.

**#20 — server reflection + grpcurl bonus**

`grpcio-reflection` was already a dependency and nothing used it. `serve()` now enables reflection, including in the three README solutions that contain `serve()` so pasting a solution doesn't silently remove it.

The bonus section shows `grpcurl list/describe/call` with and without a `.proto`, why `-plaintext` is needed, and that grpcurl's JSON is the tool's convenience rather than the wire format. Because grpcurl is a separate Go binary, it also shows how to query reflection with the Python package already installed — verified, returns `chat.ChatService` and `grpc.reflection.v1alpha.ServerReflection`.

**#22 — Exercise 9: metadata and interceptors** — `exercises/09_metadata_interceptors/`

A client interceptor attaching an auth token and a per-call request id, a server interceptor rejecting calls without a valid token, and one logging each call with its request id and duration.

Documents what actually bites: a client interceptor is registered **per call type** (implement only unary-unary and `GetHistory` goes out unauthenticated), `ClientCallDetails` is a read-only namedtuple, and a server interceptor returns a *handler* — rebuilt with the matching `grpc.*_rpc_method_handler` and its serializers — not a response.

Adds `poe server-intercepted`, `client-intercepted`, `test-09`.

## Verification

| Check | Result |
|---|---|
| Clean repo | 34 failed, 3 passed, 2 skipped — unchanged baseline |
| README solutions | 47 passed |
| `ruff check .` | clean, on a clean checkout *and* on the pasted solutions |
| Broadcast demo | two terminals, alice and bob see each other |
| Interceptor demo | token call OK, no-token call `UNAUTHENTICATED` |

Both bonus test modules skip until Exercise 1 is done, so the clean-repo baseline the README and CI assert is unchanged.

Also fixes an import-order slip the reflection change introduced in the README solutions, and adds `poe lint` to the `readme-solutions` CI job — the clean-repo lint job never sees pasted code.

## Note

Every status string, status code and behavioural claim in these docs was measured against a running server rather than written from memory.
