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
    # TODO: create channel to UNREACHABLE_SERVER
    # TODO: create ChatServiceStub
    # TODO: call SendMessage(..., timeout=0.2, wait_for_ready=True)
    # TODO: assert grpc.StatusCode.DEADLINE_EXCEEDED
    pytest.fail("Implement this test")


def test_invalid_argument_for_empty_content(stub):
    # TODO: call stub.SendMessage with content=""
    # TODO: assert StatusCode.INVALID_ARGUMENT
    pytest.fail("Implement this test")


def test_error_details_for_empty_content(stub):
    # TODO: call stub.SendMessage with content=""
    # TODO: assert details contain "cannot be empty"
    pytest.fail("Implement this test")
