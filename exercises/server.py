import time
import uuid
from concurrent import futures

import grpc
from grpc import StatusCode

from exercises.generated import chat_pb2, chat_pb2_grpc

# In-memory message store: room_id → list[Message]
_store: dict[str, list[chat_pb2.Message]] = {}


def _make_message(request: chat_pb2.MessageRequest) -> chat_pb2.Message:
    msg = chat_pb2.Message(
        message_id=str(uuid.uuid4()),
        room_id=request.room_id,
        user=request.user,
        content=request.content,
        timestamp=int(time.time()),
    )
    _store.setdefault(request.room_id, []).append(msg)
    return msg


class ChatServicer(chat_pb2_grpc.ChatServiceServicer):
    pass
    # TODO Exercise 02 — add the four method stubs below (each returning
    # `pass` for now): SendMessage, GetHistory, SendBulkMessages, Chat.
    # Hint: open exercises/generated/chat_pb2_grpc.py and find
    # ChatServiceServicer for the exact method signatures.

    # def SendMessage(...):
    #     # TODO Exercise 03 — implement unary RPC
    #     # 1. Validate request.content is not empty; abort with INVALID_ARGUMENT if so
    #     # 2. Call _make_message(request) to save and get a Message
    #     # 3. Return MessageResponse(message_id=..., status="ok", timestamp=...)

    # def GetHistory(...):
    #     # TODO Exercise 05 — implement server streaming
    #     # 1. Look up _store.get(request.room_id, [])
    #     # 2. Apply request.limit (0 = all)
    #     # 3. yield each Message

    # def SendBulkMessages(...):
    #     # TODO Exercise 05 — implement client streaming
    #     # 1. Iterate request_iterator
    #     # 2. Call _make_message for each request
    #     # 3. Return BulkResponse(messages_sent=..., messages_failed=...)

    # def Chat(...):
    #     # TODO Exercise 05 (bonus) — bidirectional streaming
    #     # 1. Iterate request_iterator
    #     # 2. For each request, save and yield the message back


def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on :{port}")
    server.wait_for_termination()
