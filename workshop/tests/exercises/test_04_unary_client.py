"""Exercise 04 — Unary Client + Communication.

Verifies the client you write in
`exercises/04_unary_client/client_starter.py`, not just the server.
Run: poe test-04
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import grpc
import pytest
from grpc import StatusCode

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402

_STARTER_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "04_unary_client"
    / "client_starter.py"
)


def _load_starter():
    """Load the starter script by path (it lives in a non-importable dir)."""
    spec = importlib.util.spec_from_file_location(
        "exercise_04_client_starter", _STARTER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _send(stub, room="client-test", user="alice", content="Hello!"):
    return stub.SendMessage(
        chat_pb2.MessageRequest(room_id=room, user=user, content=content)
    )


def test_client_can_send_message_and_receive_response(stub):
    resp = _send(stub)
    assert resp.message_id != ""
    assert resp.status == "ok"


def test_client_receives_unique_id_per_message(stub):
    id1 = _send(stub, room="unique-client").message_id
    id2 = _send(stub, room="unique-client").message_id
    assert id1 != id2


def test_client_gets_invalid_argument_on_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id="room", user="alice", content="")
        )
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT


def test_starter_main_sends_and_prints_result(grpc_addr, capsys, monkeypatch):
    """Run the starter's main() against the test server and check its output.

    The starter hardcodes localhost:50051, so point insecure_channel at the
    test server's address instead of requiring a server on the real port.
    """
    starter = _load_starter()

    real_channel = grpc.insecure_channel
    monkeypatch.setattr(
        starter.grpc,
        "insecure_channel",
        lambda target, *a, **kw: real_channel(grpc_addr, *a, **kw),
    )

    starter.main()

    out = capsys.readouterr().out
    assert "message_id" in out, (
        "main() should print the returned message_id — got:\n" + out
    )
    assert "status" in out, "main() should print the returned status — got:\n" + out
    assert "ok" in out, "the server returns status='ok' — got:\n" + out
