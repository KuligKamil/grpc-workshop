"""Exercise 04 — Unary Client + Communication.

Verify end-to-end communication between the client stub and the server.
Run: poe test-exercises
"""

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402


def _send(stub, room="client-test", user="alice", content="Hello!"):
    return stub.SendMessage(
        chat_pb2.MessageRequest(room_id=room, user=user, content=content)
    )


def test_client_can_send_message_and_receive_response(stub):
    resp = _send(stub)
    assert resp.message_id != ""
    assert resp.status == "ok"


def test_client_receives_unique_id_per_message(stub):
    id1 = _send(stub, room="unique-client").message_id
    id2 = _send(stub, room="unique-client").message_id
    assert id1 != id2


def test_client_gets_invalid_argument_on_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id="room", user="alice", content="")
        )
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

