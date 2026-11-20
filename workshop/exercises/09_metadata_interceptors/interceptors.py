"""Exercise 9 (bonus) — metadata and interceptors.

Reference implementation of the two things every real gRPC deployment needs:

* **metadata** — per-call key/value headers, gRPC's equivalent of HTTP headers,
  used for auth tokens, request ids, tracing.
* **interceptors** — middleware that wraps every call, so cross-cutting
  concerns live in one place instead of in each method.

Run it:

    poe server-intercepted      # terminal 1
    poe client-intercepted      # terminal 2
"""

import logging
import time
import uuid
from concurrent import futures

import grpc

from exercises.generated import chat_pb2, chat_pb2_grpc

TOKEN = "workshop-secret"          # a stand-in for a real credential
AUTH_KEY = "authorization"
REQUEST_ID_KEY = "x-request-id"

logger = logging.getLogger("interceptors")


# ─────────────────────────────── client side ────────────────────────────────


class AuthAndRequestIdInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Attach an auth token and a fresh request id to every outgoing call.

    One class implements all four interfaces because a client interceptor is
    registered per call type: without the unary-stream base, GetHistory would
    go out unintercepted.
    """

    def __init__(self, token: str = TOKEN) -> None:
        self._token = token

    def _with_metadata(self, client_call_details):
        metadata = list(client_call_details.metadata or ())
        metadata.append((AUTH_KEY, f"Bearer {self._token}"))
        metadata.append((REQUEST_ID_KEY, str(uuid.uuid4())))
        # _replace: ClientCallDetails is a namedtuple and is read-only.
        return client_call_details._replace(metadata=metadata)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return continuation(self._with_metadata(client_call_details), request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return continuation(self._with_metadata(client_call_details), request)

    def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        return continuation(self._with_metadata(client_call_details), request_iterator)

    def intercept_stream_stream(
        self, continuation, client_call_details, request_iterator
    ):
        return continuation(self._with_metadata(client_call_details), request_iterator)


# ─────────────────────────────── server side ────────────────────────────────


class AuthInterceptor(grpc.ServerInterceptor):
    """Reject any call that does not carry a valid token.

    A server interceptor sees the call before the servicer does, so one check
    covers every method — including ones added later.
    """

    def __init__(self, token: str = TOKEN) -> None:
        self._token = token
        self._deny = grpc.unary_unary_rpc_method_handler(
            lambda request, context: context.abort(
                grpc.StatusCode.UNAUTHENTICATED, "Missing or invalid token"
            )
        )

    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata or ())
        if metadata.get(AUTH_KEY) != f"Bearer {self._token}":
            return self._deny
        return continuation(handler_call_details)


class LoggingInterceptor(grpc.ServerInterceptor):
    """Log each call with its request id and how long it took."""

    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata or ())
        request_id = metadata.get(REQUEST_ID_KEY, "-")
        method = handler_call_details.method
        started = time.monotonic()

        handler = continuation(handler_call_details)
        if handler is None:
            return handler

        def _wrap(behavior, is_streaming):
            def unary(request, context):
                try:
                    return behavior(request, context)
                finally:
                    elapsed = (time.monotonic() - started) * 1000
                    logger.info("%s %s %.1fms", request_id, method, elapsed)

            def streaming(request, context):
                try:
                    yield from behavior(request, context)
                finally:
                    elapsed = (time.monotonic() - started) * 1000
                    logger.info("%s %s %.1fms (stream)", request_id, method, elapsed)

            return streaming if is_streaming else unary

        # Rebuild the handler, keeping its serializers and its call type.
        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                _wrap(handler.unary_unary, False),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                _wrap(handler.unary_stream, True),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                _wrap(handler.stream_unary, False),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return grpc.stream_stream_rpc_method_handler(
            _wrap(handler.stream_stream, True),
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )


# ──────────────────────────────── runnable ──────────────────────────────────


def serve(port: int = 50051) -> None:
    """Start the normal chat server, with both interceptors attached."""
    from exercises.server import ChatServicer

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(LoggingInterceptor(), AuthInterceptor()),
    )
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    try:
        server.start()
        print(f"intercepted server listening on :{port} (token: {TOKEN})")
        server.wait_for_termination()
    finally:
        server.stop(grace=5)


def demo_client(target: str = "localhost:50051") -> None:
    """Send one call with a token and one without, and show the difference."""
    print("\n[with token]")
    channel = grpc.intercept_channel(
        grpc.insecure_channel(target), AuthAndRequestIdInterceptor()
    )
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        response = stub.SendMessage(
            chat_pb2.MessageRequest(room_id="general", user="alice", content="hello")
        )
        print(f"  ok: id={response.message_id} status={response.status}")

    print("\n[without token]")
    with grpc.insecure_channel(target) as plain:
        stub = chat_pb2_grpc.ChatServiceStub(plain)
        try:
            stub.SendMessage(
                chat_pb2.MessageRequest(room_id="general", user="bob", content="hi")
            )
            print("  unexpected success")
        except grpc.RpcError as error:
            print(f"  rejected: {error.code().name}: {error.details()}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    if "--serve" in sys.argv:
        serve()
    else:
        demo_client()
