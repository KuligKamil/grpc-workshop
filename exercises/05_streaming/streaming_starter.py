"""Exercise 5 — experiment with all four gRPC streaming patterns.

Run your server first:
    poe server

Then run this script:
    poe starter-05
"""

import grpc

from exercises.generated import chat_pb2, chat_pb2_grpc

CHANNEL = "localhost:50051"


def demo_unary(stub: chat_pb2_grpc.ChatServiceStub) -> None:
    """Already working — just run it."""
    resp = stub.SendMessage(
        chat_pb2.MessageRequest(room_id="demo", user="alice", content="Hello!")
    )
    print(f"[Unary] Sent: id={resp.message_id}")


def demo_server_streaming(stub: chat_pb2_grpc.ChatServiceStub) -> None:
    """TODO: call GetHistory and print each message."""
    print("\n[Server streaming] GetHistory:")

    # First send a few messages so there is something to fetch
    for i in range(3):
        stub.SendMessage(
            chat_pb2.MessageRequest(room_id="demo", user="alice", content=f"msg {i}")
        )

    # TODO: call stub.GetHistory with a HistoryRequest
    # TODO: iterate the result and print each message


def demo_client_streaming(stub: chat_pb2_grpc.ChatServiceStub) -> None:
    """TODO: send 5 messages in a single client-streaming call."""
    print("\n[Client streaming] SendBulkMessages:")

    # TODO: define a generator that yields 5 MessageRequests
    # hint: use a for loop and chat_pb2.MessageRequest()
    def messages():
        pass
        
    # TODO: call stub.SendBulkMessages(messages()) and print the result


def demo_bidirectional(stub: chat_pb2_grpc.ChatServiceStub) -> None:
    """TODO: teach and test bidirectional streaming behavior.

    Phase A (required):
    - stream 3 requests from `inputs`
    - prefix each payload with a sequence number (#1, #2, #3)
    - print each streamed response as it arrives

    Phase B (bonus):
    - add a tiny delay between yielded requests (simulate live chat)
    - print when request generator is exhausted (client half-close)
    - pass timeout to `stub.Chat(..., timeout=...)`
    - catch `grpc.RpcError` and print code/details
    """
    print("\n[Bidirectional] Chat:")
    inputs = ["Hi there!", "How does gRPC work?", "Thanks, goodbye!"]

    # TODO: define a generator that yields one MessageRequest per input
    # hint: use enumerate() to attach a sequence number to each message content
    # bonus: pause briefly between yields — what changes in the output?
    # bonus: signal explicitly when the generator is done (client half-close)
    def requests():
        pass

    # TODO: call stub.Chat() with the generator and iterate the replies
    # bonus: pass a timeout — what happens when it expires?
    # bonus: wrap iteration in try/except grpc.RpcError and inspect the error


def main():
    with grpc.insecure_channel(CHANNEL) as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        demo_unary(stub)
        demo_server_streaming(stub)
        demo_client_streaming(stub)
        demo_bidirectional(stub)


if __name__ == "__main__":
    main()
