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
four methods (all return `pass` for now):

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

## ✅ Micro-check

You should see exactly this line in the terminal:

```
gRPC server listening on :50051
```

If the server crashes on import, a method name is probably misspelled — check
against the signatures in the **Context** section above.
If it prints `unimplemented` when you call it, the stub is wired correctly —
that's the expected placeholder response from gRPC.

## Solution

`solutions/02_service_stub/server.py`
