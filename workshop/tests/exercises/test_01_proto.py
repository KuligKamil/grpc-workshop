"""Exercise 01 — Protocol Buffers.

Verify that the compiled proto schema has the correct message types and fields.
Run: poe test-exercises
"""

import pytest


def test_message_request_has_correct_fields():
    # TODO: create a MessageRequest with room_id="r", user="u", content="c"
    # TODO: assert each field has the expected value
    pytest.fail("Implement this test")


def test_message_response_has_correct_fields():
    # TODO: create a MessageResponse with message_id="id", status="ok", timestamp=1
    # TODO: assert each field has the expected value
    pytest.fail("Implement this test")


def test_history_request_has_correct_fields():
    # TODO: create a HistoryRequest with room_id="room", limit=5
    # TODO: assert each field has the expected value
    pytest.fail("Implement this test")


def test_message_has_all_five_fields():
    # TODO: create a Message with all 5 fields: message_id, room_id, user, content, timestamp
    # TODO: assert each field has the expected value
    pytest.fail("Implement this test")


def test_stub_has_all_four_rpc_methods(stub):
    # TODO: assert that stub has methods: SendMessage, GetHistory, SendBulkMessages, Chat
    pytest.fail("Implement this test")
