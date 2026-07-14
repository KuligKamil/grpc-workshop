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
    assert issubclass(ChatServicer, chat_pb2_grpc.ChatServiceServicer)


def test_chatservicer_has_send_message():
    assert callable(getattr(ChatServicer, "SendMessage", None))


def test_chatservicer_has_get_history():
    assert callable(getattr(ChatServicer, "GetHistory", None))


def test_chatservicer_has_send_bulk_messages():
    assert callable(getattr(ChatServicer, "SendBulkMessages", None))


def test_chatservicer_has_chat():
    assert callable(getattr(ChatServicer, "Chat", None))


def test_chatservicer_can_be_instantiated():
    assert ChatServicer() is not None
