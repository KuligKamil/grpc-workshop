"""Exercise 06 — Deadlines and Error Handling.

Complete Exercise 06 and make these tests pass.
Run: poe test-exercises
"""

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2, chat_pb2_grpc  # noqa: E402


UNREACHABLE_SERVER = "localhost:50099"


def test_deadline_exceeded_on_unreachable_server():
    channel = grpc.aio.insecure_channel(UNREACHABLE_SERVER)
    stub = chat_pb2_grpc.ChatServiceStub(channel)
    
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.Message(content="test"), timeout=0.2, wait_for_ready=True)
    
    assert exc_info.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED


def test_invalid_argument_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.Message(content=""))
    
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_error_details_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.Message(content=""))
    
    assert "cannot be empty" in exc_info.value.details()
