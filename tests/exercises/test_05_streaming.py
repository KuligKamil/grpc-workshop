"""Exercise 05 — Streaming RPCs.

Implement GetHistory, SendBulkMessages and Chat in exercises/server.py, then make these pass.
Run: poe test-exercises
"""
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402


def test_get_history_returns_sent_messages(stub):
    # TODO: send 3 messages to a room using stub.SendMessage
    # TODO: call stub.GetHistory with HistoryRequest(room_id=..., limit=10)
    # TODO: assert there are 3 messages
    # TODO: assert their content matches what you sent
    pytest.fail("Implement this test")


def test_get_history_respects_limit(stub):
    # TODO: send 5 messages to a room
    # TODO: call GetHistory with limit=2
    # TODO: assert you get exactly 2 messages (the last 2)
    # TODO: assert their content matches the last 2 messages you sent
    pytest.fail("Implement this test")


def test_get_history_empty_room_returns_nothing(stub):
    # TODO: call GetHistory for a room that has no messages
    # TODO: assert the result is an empty list
    pytest.fail("Implement this test")


def test_send_bulk_messages_returns_correct_count(stub):
    # TODO: create a generator yielding 5 MessageRequests
    # TODO: call stub.SendBulkMessages(generator)
    # TODO: assert the response has 5 messages sent
    # TODO: assert the response has 0 messages failed
    pytest.fail("Implement this test")


def test_chat_echoes_messages_back(stub):
    # TODO: create a generator yielding 3 MessageRequests
    # TODO: call stub.Chat(generator) and collect replies
    # TODO: assert you get 3 replies back
    # TODO: assert the content of the replies matches what you sent
    pytest.fail("Implement this test")
