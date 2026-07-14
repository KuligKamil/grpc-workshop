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


def test_client_can_send_message_and_receive_response(stub):
    # TODO: call stub.SendMessage with a valid MessageRequest
    # TODO: assert response.message_id != ""
    # TODO: assert response.status == "ok"
    pytest.fail("Implement this test")


def test_client_receives_unique_id_per_message(stub):
    # TODO: send two messages to the same room
    # TODO: assert the two message_ids are different
    pytest.fail("Implement this test")


def test_client_gets_invalid_argument_on_empty_content(stub):
    # TODO: use pytest.raises(grpc.RpcError)
    # TODO: send a message with content=""
    # TODO: assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    pytest.fail("Implement this test")
