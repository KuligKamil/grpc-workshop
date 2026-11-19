"""Exercise 05 — Streaming RPCs.

Implement GetHistory, SendBulkMessages and Chat in exercises/server.py,
then make these pass.
Run: poe test-exercises
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402

_STARTER_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "05_streaming"
    / "streaming_starter.py"
)


def _load_starter():
    """Load the starter script by path (it lives in a non-importable dir)."""
    spec = importlib.util.spec_from_file_location(
        "exercise_05_streaming_starter", _STARTER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_bulk_messages_are_readable_by_get_history(stub):
    """Bulk-uploaded messages must come back out of GetHistory.

    Guards against storing something that is not a Message (e.g. appending
    a literal `...` to the store): SendBulkMessages still reports success,
    but GetHistory then fails to serialize the room.
    """
    room = "sol-bulk-history"

    def _requests():
        for i in range(3):
            yield chat_pb2.MessageRequest(
                room_id=room, user="alice", content=f"bulk {i}"
            )

    assert stub.SendBulkMessages(_requests()).messages_sent == 3

    messages = list(stub.GetHistory(chat_pb2.HistoryRequest(room_id=room, limit=10)))
    assert [m.content for m in messages] == ["bulk 0", "bulk 1", "bulk 2"]


def test_starter_demo_server_streaming_prints_history(stub, capsys):
    """demo_server_streaming() should print the messages it fetched back."""
    starter = _load_starter()
    starter.demo_server_streaming(stub)

    out = capsys.readouterr().out
    assert "msg 0" in out and "msg 2" in out, (
        "demo_server_streaming() should print each streamed message — got:\n" + out
    )


def test_starter_demo_client_streaming_prints_count(stub, capsys):
    """demo_client_streaming() should send 5 messages and print the result."""
    starter = _load_starter()
    starter.demo_client_streaming(stub)

    out = capsys.readouterr().out
    assert "5" in out, (
        "demo_client_streaming() should print how many messages were sent — got:\n"
        + out
    )


def test_starter_demo_bidirectional_prints_replies(stub, capsys):
    """demo_bidirectional() should print the replies streamed back."""
    starter = _load_starter()
    starter.demo_bidirectional(stub)

    out = capsys.readouterr().out
    assert out.strip(), "demo_bidirectional() should print the streamed replies"
    assert "Hi there!" in out, (
        "demo_bidirectional() should stream the `inputs` and print replies — got:\n"
        + out
    )
