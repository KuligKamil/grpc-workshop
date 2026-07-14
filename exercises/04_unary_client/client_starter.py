"""Exercise 4 — write a unary gRPC client and verify communication."""

import grpc

from exercises.generated import chat_pb2, chat_pb2_grpc


def main():
    # TODO 1: open a channel to localhost:50051 (use a context manager)
    with grpc.insecure_channel(...) as channel:

        # TODO 2: create a stub
        stub = chat_pb2_grpc.ChatServiceStub(...)

        try:
            # TODO 3: call stub.SendMessage with a MessageRequest
            response = stub.SendMessage(
                chat_pb2.MessageRequest(
                    room_id=...,   # e.g. "general"
                    user=...,      # e.g. "alice"
                    content=...,   # e.g. "Hello EuroPython!"
                )
            )

            # TODO 4: print message_id and status

        except grpc.RpcError as e:
            # TODO 5: print the error code and details
            pass


if __name__ == "__main__":
    main()
