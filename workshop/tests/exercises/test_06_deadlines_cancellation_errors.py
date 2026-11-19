"""Exercise 06 — Deadlines and Error Handling.

Verifies the demos you write in
`exercises/06_deadlines_cancellation_errors/deadlines_starter.py`.
Run: poe test-06
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2  # noqa: E402

_STARTER_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "06_deadlines_cancellation_errors"
    / "deadlines_starter.py"
)


def _load_starter():
    """Load the starter script by path (it lives in a non-importable dir)."""
    spec = importlib.util.spec_from_file_location(
        "exercise_06_deadlines_starter", _STARTER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_starter_demo_deadline_exceeded_prints_code(capsys):
    """demo_deadline_exceeded() should catch the error and print its code."""
    starter = _load_starter()
    starter.demo_deadline_exceeded()

    out = capsys.readouterr().out
    assert "DEADLINE_EXCEEDED" in out, (
        "demo_deadline_exceeded() should print the status code of the error "
        "it caught — got:\n" + out
    )


def test_starter_demo_invalid_argument_prints_code_and_details(
    grpc_addr, capsys, monkeypatch
):
    """demo_invalid_argument() should print both the code and the details."""
    starter = _load_starter()

    # The starter targets EXERCISE_SERVER (localhost:50051); point it at the
    # test server so no manually started server is required.
    monkeypatch.setattr(starter, "EXERCISE_SERVER", grpc_addr, raising=False)

    starter.demo_invalid_argument()

    out = capsys.readouterr().out
    assert "INVALID_ARGUMENT" in out, (
        "demo_invalid_argument() should print the status code — got:\n" + out
    )
    assert "cannot be empty" in out, (
        "demo_invalid_argument() should print error.details() — got:\n" + out
    )


def test_invalid_argument_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.MessageRequest(content=""))

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_error_details_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.MessageRequest(content=""))

    assert "cannot be empty" in exc_info.value.details()
