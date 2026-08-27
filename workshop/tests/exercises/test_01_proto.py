"""Exercise 01 — Protocol Buffers.

Verify that the compiled proto schema has the correct message types and fields.
Run: poe test-exercises
"""

import pytest
from google.protobuf import timestamp_pb2

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402


def test_message_response_has_correct_fields():
    ts = timestamp_pb2.Timestamp(seconds=1)
    msg = chat_pb2.MessageResponse(message_id="id", status="ok", timestamp=ts)
    assert msg.message_id == "id"
    assert msg.status == "ok"
    assert msg.timestamp == ts


def test_history_request_has_correct_fields():
    msg = chat_pb2.HistoryRequest(room_id="room", limit=5)
    assert msg.room_id == "room"
    assert msg.limit == 5


def test_message_has_all_five_fields():
    ts = timestamp_pb2.Timestamp(seconds=1)
    msg = chat_pb2.Message(
        message_id="id", room_id="r", user="u", content="c", timestamp=ts
    )
    assert msg.message_id == "id"
    assert msg.room_id == "r"
    assert msg.user == "u"
    assert msg.content == "c"
    assert msg.timestamp == ts
