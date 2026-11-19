"""Exercise 8 (bonus) — a real chat: broadcast messages to everyone in a room.

Reference implementation. Until now `Chat` echoed each message back to its
sender, so two clients in the same room never saw each other. Here every
message is fanned out to all participants.

Run it instead of the normal server:

    poe server-broadcast

Then open two terminals and talk to each other:

    poe final-chat --room general --user alice
    poe final-chat --room general --user bob
"""

import queue
import threading
import uuid
from concurrent import futures

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import StatusCode

from exercises.generated import chat_pb2, chat_pb2_grpc

# In-memory message store: room_id → list[Message]
_store: dict[str, list[chat_pb2.Message]] = {}

# Live subscribers: room_id → one queue per connected Chat stream.
_rooms: dict[str, list[queue.Queue]] = {}

# Guards both dicts: gRPC serves each call on its own thread.
_lock = threading.Lock()

# Sentinel telling a stream that its sender is finished.
_DONE = object()


def _make_message(request: chat_pb2.MessageRequest) -> chat_pb2.Message:
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    msg = chat_pb2.Message(
        message_id=str(uuid.uuid4()),
        room_id=request.room_id,
        user=request.user,
        content=request.content,
        timestamp=timestamp,
    )
    with _lock:
        _store.setdefault(request.room_id, []).append(msg)
    return msg


class BroadcastChatServicer(chat_pb2_grpc.ChatServiceServicer):
    def SendMessage(self, request, context):
        """Unary — also delivered to anyone currently in the room."""
        if not request.content:
            context.abort(
                StatusCode.INVALID_ARGUMENT, "Message content cannot be empty"
            )
        msg = _make_message(request)
        _broadcast(msg)
        return chat_pb2.MessageResponse(
            message_id=msg.message_id,
            status="ok",
            timestamp=msg.timestamp,
        )

    def GetHistory(self, request, context):
        with _lock:
            messages = list(_store.get(request.room_id, ()))
        limit = request.limit if request.limit > 0 else len(messages)
        for msg in messages[-limit:]:
            yield msg

    def SendBulkMessages(self, request_iterator, context):
        sent = 0
        failed = 0
        for request in request_iterator:
            if not request.content:
                failed += 1
                continue
            _broadcast(_make_message(request))
            sent += 1
        return chat_pb2.BulkResponse(messages_sent=sent, messages_failed=failed)

    def Chat(self, request_iterator, context):
        """Bidirectional streaming — fan every message out to the whole room.

        Each stream gets its own queue. Reading the client's requests and
        writing replies have to happen at the same time, so the reading runs
        on a separate thread while this generator drains the queue.
        """
        inbox: queue.Queue = queue.Queue()
        # The room is unknown until the first request arrives.
        room_id: str | None = None

        def _unsubscribe() -> None:
            if room_id is None:
                return
            with _lock:
                subscribers = _rooms.get(room_id)
                if subscribers and inbox in subscribers:
                    subscribers.remove(inbox)
                if subscribers is not None and not subscribers:
                    del _rooms[room_id]

        # Runs however the call ends — normally, cancelled, or disconnected.
        # Without it, queues for dead clients would pile up forever.
        context.add_callback(_unsubscribe)

        def _receive() -> None:
            nonlocal room_id
            try:
                for request in request_iterator:
                    if not request.content:
                        continue
                    if room_id is None:
                        room_id = request.room_id
                        with _lock:
                            _rooms.setdefault(room_id, []).append(inbox)
                    _broadcast(_make_message(request))
            except grpc.RpcError:
                # The client hung up mid-stream; that is a normal way to leave.
                pass
            finally:
                inbox.put(_DONE)   # wake our own stream so it can finish

        threading.Thread(target=_receive, daemon=True).start()

        while True:
            item = inbox.get()
            if item is _DONE:
                return
            yield item


def _broadcast(msg: chat_pb2.Message) -> None:
    """Deliver a message to every stream subscribed to its room."""
    with _lock:
        targets = list(_rooms.get(msg.room_id, ()))
    for target in targets:
        target.put(msg)


def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(BroadcastChatServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    try:
        server.start()
        print(f"broadcast chat server listening on :{port}")
        server.wait_for_termination()
    finally:
        server.stop(grace=5)


if __name__ == "__main__":
    serve()
