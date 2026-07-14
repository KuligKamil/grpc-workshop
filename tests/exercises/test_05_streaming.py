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


def _send(stub, room="test-room", user="alice", content="Hi!"):
    return stub.SendMessage(
        chat_pb2.MessageRequest(room_id=room, user=user, content=content)
    )


def test_get_history_returns_sent_messages(stub):
    room = "sol-history-1"
    for i in range(3):
        _send(stub, room=room, content=f"msg {i}")
    messages = list(stub.GetHistory(chat_pb2.HistoryRequest(room_id=room, limit=10)))
    assert len(messages) == 3
    assert messages[0].content == "msg 0"
    assert messages[2].content == "msg 2"


def test_get_history_respects_limit(stub):
    room = "sol-history-2"
    for i in range(5):
        _send(stub, room=room, content=f"msg {i}")
    messages = list(stub.GetHistory(chat_pb2.HistoryRequest(room_id=room, limit=2)))
    assert len(messages) == 2
    assert messages[0].content == "msg 3"
    assert messages[1].content == "msg 4"


def test_get_history_empty_room_returns_nothing(stub):
    messages = list(
        stub.GetHistory(chat_pb2.HistoryRequest(room_id="sol-empty-room", limit=10))
    )
    assert messages == []


def test_send_bulk_messages_returns_correct_count(stub):
    def _requests():
        for i in range(5):
            yield chat_pb2.MessageRequest(
                room_id="sol-bulk", user="alice", content=f"bulk {i}"
            )

    resp = stub.SendBulkMessages(_requests())
    assert resp.messages_sent == 5
    assert resp.messages_failed == 0


def test_chat_echoes_messages_back(stub):
    inputs = ["Hello", "How are you?", "Goodbye"]

    def _requests():
        for text in inputs:
            yield chat_pb2.MessageRequest(
                room_id="sol-bidi", user="alice", content=text
            )

    replies = list(stub.Chat(_requests()))
    assert len(replies) == 3
    assert [r.content for r in replies] == inputs
