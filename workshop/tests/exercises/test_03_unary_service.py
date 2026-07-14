"""Exercise 03 — Implement Unary SendMessage.

Implement ChatServicer.SendMessage in exercises/server.py, then make these tests pass.
Run: poe test-exercises
"""

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402


def test_send_message_returns_non_empty_id(stub):
    # TODO: call stub.SendMessage with MessageRequest(room_id=..., user=..., content=...)
    # TODO: assert resp.message_id != ""
    pytest.fail("Implement this test")


def test_send_message_returns_ok_status(stub):
    # TODO: call stub.SendMessage
    # TODO: assert resp.status == "ok"
    pytest.fail("Implement this test")


def test_send_message_returns_positive_timestamp(stub):
    # TODO: call stub.SendMessage
    # TODO: assert resp.timestamp > 0
    pytest.fail("Implement this test")


def test_send_message_generates_unique_ids(stub):
    # TODO: send two messages to the same room
    # TODO: assert the message_ids are different
    pytest.fail("Implement this test")


def test_empty_content_raises_invalid_argument(stub):
    # TODO: use pytest.raises(grpc.RpcError) to catch the error
    # TODO: call stub.SendMessage with content=""
    # TODO: assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    pytest.fail("Implement this test")
