# Exercise 9 (bonus): Metadata and interceptors

**Estimated time:** ~20 min

## Goal

Attach a token and a request id to every call without touching a single
servicer method.

## Metadata

Metadata is gRPC's equivalent of HTTP headers: key/value pairs travelling with
a call, separate from the message. Keys are lowercase; a key ending in `-bin`
carries bytes, anything else carries text.

Sending it, per call:

```python
stub.SendMessage(request, metadata=(("authorization", "Bearer abc"),))
```

Reading it on the server:

```python
def SendMessage(self, request, context):
    metadata = dict(context.invocation_metadata())
    token = metadata.get("authorization")
```

This is where auth tokens, request ids and tracing headers belong — not as
fields in your messages, which are about the *domain*, not the transport.

## Why interceptors

Passing `metadata=` at every call site is easy to forget, and checking the
token inside every method duplicates the check and misses methods added later.
Interceptors wrap *all* calls in one place — gRPC's middleware.

**Client side** adds the metadata:

```python
channel = grpc.intercept_channel(
    grpc.insecure_channel("localhost:50051"), AuthAndRequestIdInterceptor()
)
```

**Server side** enforces it, before the servicer runs:

```python
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=(LoggingInterceptor(), AuthInterceptor()),
)
```

## Three things that trip people up

**1. A client interceptor is per call type.** There are four separate base
classes: `UnaryUnaryClientInterceptor`, `UnaryStreamClientInterceptor`,
`StreamUnaryClientInterceptor`, `StreamStreamClientInterceptor`. Implement only
the first and your `GetHistory` quietly goes out *without* the token. The
reference implementation inherits all four for that reason.

**2. `ClientCallDetails` is read-only.** It is a namedtuple, so you copy it:

```python
metadata = list(client_call_details.metadata or ())
metadata.append(("authorization", f"Bearer {token}"))
return client_call_details._replace(metadata=metadata)
```

**3. A server interceptor returns a *handler*, not a response.** To reject a
call you return a handler that aborts; to let it through you return
`continuation(handler_call_details)`. And if you want to wrap the behaviour
(timing, logging), you must rebuild the handler with the matching
`grpc.*_rpc_method_handler` and keep its serializers — otherwise you break
serialization for that method.

## Run it

```bash
# Terminal 1
poe server-intercepted

# Terminal 2
poe client-intercepted
```

Output:

```text
[with token]
  ok: id=19df637c-… status=ok

[without token]
  rejected: UNAUTHENTICATED: Missing or invalid token
```

And on the server, one line per call — request id, method, duration:

```text
interceptors: f8c998cd-… /chat.ChatService/SendMessage 0.6ms
interceptors: -          /chat.ChatService/SendMessage 0.1ms
```

The rejected call logs `-` because it never carried a request id: the auth
interceptor stopped it first. Interceptor order is the order you pass them.

## Verify

```bash
poe test-09
```

## Going further

- Return the request id to the caller with
  `context.set_trailing_metadata(...)` so a client can log it too.
- Real auth uses TLS plus `grpc.access_token_call_credentials`, so the token
  is not readable on the wire — `insecure_channel` here is for the workshop
  only.
- An interceptor is the natural place for retries, rate limiting and metrics.
