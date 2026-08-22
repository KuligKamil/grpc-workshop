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
    # Must be defined on ChatServicer itself, not just inherited from the
    # generated base class (which already provides UNIMPLEMENTED stubs).
    assert "SendMessage" in vars(ChatServicer)
    assert callable(ChatServicer.SendMessage)


def test_chatservicer_has_get_history():
    assert "GetHistory" in vars(ChatServicer)
    assert callable(ChatServicer.GetHistory)


def test_chatservicer_has_send_bulk_messages():
    assert "SendBulkMessages" in vars(ChatServicer)
    assert callable(ChatServicer.SendBulkMessages)


def test_chatservicer_has_chat():
    assert "Chat" in vars(ChatServicer)
    assert callable(ChatServicer.Chat)


def test_chatservicer_can_be_instantiated():
    assert ChatServicer() is not None
