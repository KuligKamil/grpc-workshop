"""Exercise 01 — Protocol Buffers.

Verify that the compiled proto schema has the correct message types and fields.
Run: poe test-exercises
"""

import pytest

from exercises.generated import chat_pb2


def test_message_request_has_correct_fields():
    msg = chat_pb2.MessageRequest(room_id="r", user="u", content="c")
    assert msg.room_id == "r"
    assert msg.user == "u"
    assert msg.content == "c"


def test_message_response_has_correct_fields():
    msg = chat_pb2.MessageResponse(message_id="id", status="ok", timestamp=1)
    assert msg.message_id == "id"
    assert msg.status == "ok"
    assert msg.timestamp == 1


def test_history_request_has_correct_fields():
    msg = chat_pb2.HistoryRequest(room_id="room", limit=5)
    assert msg.room_id == "room"
    assert msg.limit == 5


def test_message_has_all_five_fields():
    msg = chat_pb2.Message(
        message_id="id", room_id="r", user="u", content="c", timestamp=1
    )
    assert msg.message_id == "id"
    assert msg.room_id == "r"
    assert msg.user == "u"
    assert msg.content == "c"
    assert msg.timestamp == 1
