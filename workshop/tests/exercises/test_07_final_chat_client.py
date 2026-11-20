"""Exercise 07 — Final chat client in client.py.

Implement `send`, `history`, and `chat` in
`exercises/07_final_chat_client/client.py` using knowledge from
Exercises 05 and 06.
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

_CLIENT_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "07_final_chat_client"
    / "client.py"
)


def _load_client_module():
    spec = importlib.util.spec_from_file_location(
        "exercise_07_final_chat_client", _CLIENT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = _load_client_module()


def _split_addr(grpc_addr: str) -> tuple[str, int]:
    host, port = grpc_addr.rsplit(":", maxsplit=1)
    return host, int(port)


def test_send_command_prints_success(grpc_addr, capsys):
    host, port = _split_addr(grpc_addr)

    client.send(
        message="hello",
        room="sol-final-send",
        user="alice",
        host=host,
        port=port,
    )

    out = capsys.readouterr().out
    assert "✓ Sent" in out and "status=ok" in out, (
        "send() should print '✓ Sent  id=<id>  status=ok' — got:\n" + out
    )


def test_history_command_prints_streamed_messages(stub, grpc_addr, capsys):
    room = "sol-final-history"
    for i in range(3):
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id=room, user="alice", content=f"msg {i}")
        )

    host, port = _split_addr(grpc_addr)
    client.history(room=room, limit=10, host=host, port=port)

    out = capsys.readouterr().out
    assert "[alice] msg 0" in out and "[alice] msg 2" in out, (
        "history() should print each message as '[user] content' — got:\n" + out
    )


def test_chat_command_streams_and_prints_replies(grpc_addr, capsys, monkeypatch):
    host, port = _split_addr(grpc_addr)
    user_inputs = iter(["hello", "from chat", EOFError()])

    def fake_input(_prompt: str = ""):
        value = next(user_inputs)
        if isinstance(value, BaseException):
            raise value
        return value

    monkeypatch.setattr("builtins.input", fake_input)
    client.chat(room="sol-final-chat", user="alice", host=host, port=port)

    out = capsys.readouterr().out
    assert "← [alice] hello" in out and "← [alice] from chat" in out, (
        "chat() should print each reply as '  ← [user] content' — got:\n" + out
    )

