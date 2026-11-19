"""Exercise 09 (bonus) — metadata and interceptors.

Run: poe test-09
"""

from __future__ import annotations

import importlib.util
from concurrent import futures
from pathlib import Path

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2, chat_pb2_grpc  # noqa: E402

if not chat_pb2.Message.DESCRIPTOR.fields_by_name.get("message_id"):
    pytest.skip(
        "Complete Exercise 01 (Message fields) before the interceptor bonus",
        allow_module_level=True,
    )

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "09_metadata_interceptors"
    / "interceptors.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "exercise_09_interceptors", _MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _EchoServicer(chat_pb2_grpc.ChatServiceServicer):
    """Minimal servicer: enough to prove the interceptors ran."""

    def __init__(self) -> None:
        self.seen_metadata: list[tuple[str, str]] = []

    def SendMessage(self, request, context):
        self.seen_metadata = list(context.invocation_metadata())
        return chat_pb2.MessageResponse(message_id="fixed-id", status="ok")

    def GetHistory(self, request, context):
        self.seen_metadata = list(context.invocation_metadata())
        yield chat_pb2.Message(message_id="m1", content="one")


@pytest.fixture
def intercepted():
    module = _load()
    servicer = _EchoServicer()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        interceptors=(module.LoggingInterceptor(), module.AuthInterceptor()),
    )
    chat_pb2_grpc.add_ChatServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("[::]:0")
    try:
        server.start()
        yield module, servicer, f"localhost:{port}"
    finally:
        server.stop(grace=None)


def _request():
    return chat_pb2.MessageRequest(room_id="general", user="alice", content="hi")


def test_call_with_token_succeeds(intercepted):
    module, _servicer, addr = intercepted
    channel = grpc.intercept_channel(
        grpc.insecure_channel(addr), module.AuthAndRequestIdInterceptor()
    )
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        assert stub.SendMessage(_request()).status == "ok"


def test_call_without_token_is_unauthenticated(intercepted):
    _module, _servicer, addr = intercepted
    with grpc.insecure_channel(addr) as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.SendMessage(_request())
    assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED


def test_call_with_wrong_token_is_unauthenticated(intercepted):
    module, _servicer, addr = intercepted
    channel = grpc.intercept_channel(
        grpc.insecure_channel(addr),
        module.AuthAndRequestIdInterceptor(token="not-the-token"),
    )
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.SendMessage(_request())
    assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED


def test_interceptor_attaches_auth_and_request_id(intercepted):
    module, servicer, addr = intercepted
    channel = grpc.intercept_channel(
        grpc.insecure_channel(addr), module.AuthAndRequestIdInterceptor()
    )
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        stub.SendMessage(_request())

    received = dict(servicer.seen_metadata)
    assert received[module.AUTH_KEY] == f"Bearer {module.TOKEN}"
    assert received[module.REQUEST_ID_KEY], "a request id should be attached"


def test_each_call_gets_a_fresh_request_id(intercepted):
    module, servicer, addr = intercepted
    channel = grpc.intercept_channel(
        grpc.insecure_channel(addr), module.AuthAndRequestIdInterceptor()
    )
    seen = []
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        for _ in range(2):
            stub.SendMessage(_request())
            seen.append(dict(servicer.seen_metadata)[module.REQUEST_ID_KEY])
    assert seen[0] != seen[1]


def test_streaming_calls_are_intercepted_too(intercepted):
    """unary_stream needs its own interceptor interface — easy to forget."""
    module, servicer, addr = intercepted
    channel = grpc.intercept_channel(
        grpc.insecure_channel(addr), module.AuthAndRequestIdInterceptor()
    )
    with channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        messages = list(
            stub.GetHistory(chat_pb2.HistoryRequest(room_id="general", limit=5))
        )
    assert [m.content for m in messages] == ["one"]
    assert dict(servicer.seen_metadata)[module.AUTH_KEY] == f"Bearer {module.TOKEN}"
