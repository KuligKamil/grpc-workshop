# Exercise 2: Build a Service Stub 

## Goal

Add the `ChatServicer` method stubs — the Python object that will handle
incoming gRPC calls. In this exercise you only need the **structure** (no
logic yet).

## Context

After running `poe generate-exercises`, grpc_tools produced
`exercises/generated/chat_pb2_grpc.py`. Open it and find
`ChatServiceServicer` — this is the base class `ChatServicer` already
inherits from in `exercises/server.py`.

The generated base class defines these exact method signatures:

```python
def SendMessage(self, request, context):
	...

def GetHistory(self, request, context):
	...

def SendBulkMessages(self, request_iterator, context):
	...

def Chat(self, request_iterator, context):
	...
```

## Your task

Open `exercises/server.py` and, inside the `ChatServicer` class, add these
four methods, each with a body of just `pass` for now:

- `SendMessage(self, request, context)`
- `GetHistory(self, request, context)`
- `SendBulkMessages(self, request_iterator, context)`
- `Chat(self, request_iterator, context)`

The class already inherits from `chat_pb2_grpc.ChatServiceServicer`, and it's
already registered with the server in `serve()` — you only need to add the
method stubs.

## Run it

```bash
poe server
# gRPC server listening on :50051
# Ctrl-C to stop
```

The server starts but returns gRPC errors on every call — that's expected.
We'll add the real logic in Exercise 3.

## Verify

Run just this exercise's tests (regenerates the stubs first):

```bash
poe test-02
```

`poe test-exercises` runs all of them.

## ✅ Micro-check

You should see exactly this line in the terminal:

```
gRPC server listening on :50051
```

If the server crashes on start, look at the traceback — usually a
`SyntaxError` or `IndentationError` in `server.py`. A *misspelled* method
name does **not** crash anything: the server starts fine and that method
answers `UNIMPLEMENTED` (see the table below).
Now call it (`poe client-send --room general --user alice "Hello!"`). You get:

```
✗ StatusCode.INTERNAL: Failed to serialize response!
```

That error means the stub is wired correctly. Your method ran — it just
returned `None`, and gRPC could not serialize `None` into a `MessageResponse`.

It is worth knowing the difference, because the two look similar but mean
opposite things:

| Servicer state | Unary call | Streaming call |
|---|---|---|
| method defined, body is `pass` | `INTERNAL: Failed to serialize response!` | `UNKNOWN: Exception iterating responses: 'NoneType' object is not an iterator` |
| method not defined at all | `UNIMPLEMENTED: Method not implemented!` | `UNIMPLEMENTED: Method not implemented!` |

So `UNIMPLEMENTED` means gRPC never found your method (check the spelling
against the generated base class); `INTERNAL`/`UNKNOWN` means it found and ran
it, but you have not returned anything yet. We fix that in Exercise 3.

## What's inside the generated `chat_pb2_grpc.py`

You never edit this file, but reading it explains most of gRPC's behaviour.
Open `exercises/generated/chat_pb2_grpc.py` and find these three things.

**1. `ChatServiceStub` — the client side.** Its `__init__` turns each RPC into a
callable, and the *method it uses* encodes the pattern straight from
`chat.proto`:

```python
self.SendMessage      = channel.unary_unary(...)    # 1 in  → 1 out
self.GetHistory       = channel.unary_stream(...)   # 1 in  → N out
self.SendBulkMessages = channel.stream_unary(...)   # N in  → 1 out
self.Chat             = channel.stream_stream(...)  # N in  → N out
```

This is why `stub.SendMessage(...)` returns a response object while
`stub.GetHistory(...)` returns something you iterate: they are built by
different channel methods. Each one also gets the serializer pair for its
message types, which is why a stub only speaks `chat.proto`.

**2. `ChatServiceServicer` — the server side you inherit from.** Every method is
a placeholder that does exactly this:

```python
def SendMessage(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')
```

That is the whole mystery behind `UNIMPLEMENTED: Method not implemented!` — it
is not gRPC noticing a gap, it is this generated method running because your
subclass didn't override it. Override it with a body of `pass` and you get
`INTERNAL` or `UNKNOWN` instead, because now *your* code runs and returns
nothing.

**3. `add_ChatServiceServicer_to_server` — the wiring.** It builds a dict from
method name to a handler that pairs your function with the right
serializer/deserializer:

```python
'SendMessage': grpc.unary_unary_rpc_method_handler(
        servicer.SendMessage,
        request_deserializer=chat__pb2.MessageRequest.FromString,
        response_serializer=chat__pb2.MessageResponse.SerializeToString,
),
```

Two consequences worth remembering:

- **Method names are looked up as strings**, so a typo (`send_message`,
  `SendMesage`) does not fail loudly — gRPC just never finds your method and
  the generated placeholder answers `UNIMPLEMENTED`.
- **`response_serializer` is applied to whatever you return.** Return `None` and
  serialization fails with `INTERNAL: Failed to serialize response!`, which is
  the error from Exercise 2.

There is also a `ChatService` class at the bottom using
`grpc.experimental.*`. It is an experimental one-shot call API — ignore it, the
workshop uses the stub.
