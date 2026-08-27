"""Exercise 06 — Deadlines and Error Handling.

Complete Exercise 06 and make these tests pass.
Run: poe test-exercises
"""

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


def _load_starter_module():
    spec = importlib.util.spec_from_file_location(
        "exercise_06_deadlines_starter", _STARTER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_deadline_exceeded_reports_deadline_exceeded(capsys):
    """demo_deadline_exceeded() must call the unreachable server and print
    DEADLINE_EXCEEDED — this fails until deadlines_starter.py is implemented."""
    starter = _load_starter_module()

    starter.demo_deadline_exceeded()

    captured = capsys.readouterr()
    assert "DEADLINE_EXCEEDED" in captured.out


def test_demo_invalid_argument_reports_invalid_argument(grpc_addr, monkeypatch, capsys):
    """demo_invalid_argument() must call SendMessage with empty content against
    the exercise server and print INVALID_ARGUMENT plus the error details."""
    starter = _load_starter_module()
    monkeypatch.setattr(starter, "EXERCISE_SERVER", grpc_addr)

    starter.demo_invalid_argument()

    captured = capsys.readouterr()
    assert "INVALID_ARGUMENT" in captured.out
    assert "cannot be empty" in captured.out


def test_invalid_argument_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.MessageRequest(content=""))
    
    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_error_details_for_empty_content(stub):
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.SendMessage(chat_pb2.MessageRequest(content=""))
    
    assert "cannot be empty" in exc_info.value.details()
