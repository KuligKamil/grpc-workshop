"""Exercise 02 — Service Stub.

Verify that ChatServicer is correctly defined with the required methods.
Run: poe test-exercises
"""

import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
chat_pb2_grpc = pytest.importorskip(
    "exercises.generated.chat_pb2_grpc",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)

from exercises.server import ChatServicer  # noqa: E402


def test_chatservicer_inherits_from_generated_base():
    pytest.fail("Implement this test")


def test_chatservicer_has_send_message():
    pytest.fail("Implement this test")


def test_chatservicer_has_get_history():
    pytest.fail("Implement this test")


def test_chatservicer_has_send_bulk_messages():
    pytest.fail("Implement this test")


def test_chatservicer_has_chat():
    pytest.fail("Implement this test")


def test_chatservicer_can_be_instantiated():
    pytest.fail("Implement this test")
