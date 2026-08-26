"""Exercise 07 — Final chat client in client.py.

Implement `send`, `history`, and `chat` in
`exercises/07_final_chat_client/client.py` using knowledge from
Exercises 05 and 06.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import typer

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


def test_send_command_prints_success(grpc_addr, monkeypatch):
    host, port = _split_addr(grpc_addr)
    captured: list[str] = []

    monkeypatch.setattr(typer, "echo", lambda m, **_: captured.append(str(m)))
    client.send(
        message="hello",
        room="sol-final-send",
        user="alice",
        host=host,
        port=port,
    )

    assert any("✓ Sent" in line and "status=ok" in line for line in captured)


def test_history_command_prints_streamed_messages(stub, grpc_addr, monkeypatch):
    room = "sol-final-history"
    for i in range(3):
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id=room, user="alice", content=f"msg {i}")
        )

    host, port = _split_addr(grpc_addr)
    captured: list[str] = []
    monkeypatch.setattr(typer, "echo", lambda m, **_: captured.append(str(m)))
    client.history(room=room, limit=10, host=host, port=port)

    assert any("[alice] msg 0" in line for line in captured)
    assert any("[alice] msg 2" in line for line in captured)


def test_chat_command_streams_and_prints_replies(grpc_addr, monkeypatch):
    host, port = _split_addr(grpc_addr)
    user_inputs = iter(["hello", "from chat", EOFError()])
    captured: list[str] = []

    def fake_input(_prompt: str = ""):
        value = next(user_inputs)
        if isinstance(value, BaseException):
            raise value
        return value

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr(typer, "echo", lambda m, **_: captured.append(str(m)))
    client.chat(room="sol-final-chat", user="alice", host=host, port=port)

    assert any("Connected!" in line for line in captured)
    assert any("← [alice] hello" in line for line in captured)
    assert any("← [alice] from chat" in line for line in captured)

