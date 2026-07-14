"""Exercise 03 — Implement Unary SendMessage.

Implement ChatServicer.SendMessage in exercises/server.py, then make these tests pass.
Run: poe test-exercises
"""

import grpc
import pytest
from grpc import StatusCode


pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402


def _send(stub, room="test-room", user="alice", content="Hi!"):
    return stub.SendMessage(
        chat_pb2.MessageRequest(room_id=room, user=user, content=content)
    )


def test_send_message_returns_non_empty_id(stub):
    resp = _send(stub)
    assert resp.message_id != ""


def test_send_message_returns_ok_status(stub):
    resp = _send(stub)
    assert resp.status == "ok"


def test_send_message_returns_positive_timestamp(stub):
    resp = _send(stub)
    assert resp.timestamp > 0


def test_send_message_generates_unique_ids(stub):
    id1 = _send(stub, room="unique-sol").message_id
    id2 = _send(stub, room="unique-sol").message_id
    assert id1 != id2


def test_empty_content_raises_invalid_argument(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id="room", user="alice", content="")
        )
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT