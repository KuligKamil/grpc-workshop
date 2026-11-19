"""Exercise 08 (bonus) — broadcast chat.

Verifies that two clients in the same room see each other's messages.
Run: poe test-08
"""

from __future__ import annotations

import importlib.util
import queue
import threading
from concurrent import futures
from pathlib import Path

import grpc
import pytest

pytest.importorskip(
    "exercises.generated.chat_pb2",
    reason="Complete Exercise 01 and run: poe generate-exercises",
)
from exercises.generated import chat_pb2, chat_pb2_grpc  # noqa: E402

# This bonus builds on the finished contract, so skip until Exercise 01 is done
# rather than failing with a confusing "Message has no message_id field".
if not chat_pb2.Message.DESCRIPTOR.fields_by_name.get("message_id"):
    pytest.skip(
        "Complete Exercise 01 (Message fields) before the broadcast bonus",
        allow_module_level=True,
    )

_SERVER_PATH = (
    Path(__file__).resolve().parents[2]
    / "exercises"
    / "08_broadcast_chat"
    / "server_broadcast.py"
)


def _load_broadcast_server():
    spec = importlib.util.spec_from_file_location(
        "exercise_08_server_broadcast", _SERVER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def broadcast_addr():
    module = _load_broadcast_server()
    # Each test gets a clean store and subscriber registry.
    module._store.clear()
    module._rooms.clear()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(
        module.BroadcastChatServicer(), server
    )
    port = server.add_insecure_port("[::]:0")
    try:
        server.start()
        yield f"localhost:{port}"
    finally:
        server.stop(grace=None)


class _Participant:
    """A Chat stream driven from the test: send on demand, collect replies."""

    def __init__(self, addr: str, room: str, user: str) -> None:
        self._outbox: queue.Queue = queue.Queue()
        self.received: queue.Queue = queue.Queue()
        self.channel = grpc.insecure_channel(addr)
        stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self._stop = object()

        def _requests():
            while True:
                item = self._outbox.get()
                if item is self._stop:
                    return
                yield chat_pb2.MessageRequest(room_id=room, user=user, content=item)

        self._call = stub.Chat(_requests())
        self._reader = threading.Thread(target=self._drain, daemon=True)
        self._reader.start()

    def _drain(self) -> None:
        try:
            for reply in self._call:
                self.received.put(reply)
        except grpc.RpcError:
            pass

    def send(self, content: str) -> None:
        self._outbox.put(content)

    def next_message(self, timeout: float = 5.0) -> chat_pb2.Message:
        return self.received.get(timeout=timeout)

    def close(self) -> None:
        self._outbox.put(self._stop)
        self.channel.close()


def test_two_participants_see_each_others_messages(broadcast_addr):
    alice = _Participant(broadcast_addr, "general", "alice")
    bob = _Participant(broadcast_addr, "general", "bob")
    try:
        # Both must be subscribed before anyone speaks, and subscription
        # happens on the first message — so let each one announce itself.
        alice.send("alice joins")
        assert alice.next_message().content == "alice joins"

        bob.send("bob joins")
        # Alice sees Bob's message: that is the whole point of broadcasting.
        assert alice.next_message().content == "bob joins"
        assert bob.next_message().content == "bob joins"

        alice.send("hello bob")
        assert bob.next_message().content == "hello bob"
        assert alice.next_message().content == "hello bob"
    finally:
        alice.close()
        bob.close()


def test_messages_do_not_leak_between_rooms(broadcast_addr):
    alice = _Participant(broadcast_addr, "room-a", "alice")
    bob = _Participant(broadcast_addr, "room-b", "bob")
    try:
        alice.send("only for room-a")
        assert alice.next_message().content == "only for room-a"

        bob.send("only for room-b")
        assert bob.next_message().content == "only for room-b"

        # Bob must never have seen Alice's message.
        assert bob.received.empty()
    finally:
        alice.close()
        bob.close()


def test_subscriber_is_cleaned_up_on_disconnect(broadcast_addr):
    module = _load_broadcast_server()
    alice = _Participant(broadcast_addr, "cleanup", "alice")
    alice.send("hi")
    assert alice.next_message().content == "hi"
    alice.close()

    # add_callback runs the unsubscribe; give the server a moment to notice.
    for _ in range(50):
        if not module._rooms.get("cleanup"):
            break
        threading.Event().wait(0.1)

    assert not module._rooms.get("cleanup"), (
        "the disconnected client's queue was left registered — "
        "context.add_callback should remove it"
    )


def test_broadcast_history_still_works(broadcast_addr):
    with grpc.insecure_channel(broadcast_addr) as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        for i in range(3):
            stub.SendMessage(
                chat_pb2.MessageRequest(room_id="hist", user="alice", content=f"m{i}")
            )
        messages = list(
            stub.GetHistory(chat_pb2.HistoryRequest(room_id="hist", limit=10))
        )
    assert [m.content for m in messages] == ["m0", "m1", "m2"]
