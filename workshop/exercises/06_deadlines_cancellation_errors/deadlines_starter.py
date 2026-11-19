"""Exercise 6 — deadlines and status-aware error handling.

Run your exercise server first:
    poe server

Then run this script:
    poe starter-06
"""

import grpc

from exercises.generated import chat_pb2, chat_pb2_grpc

EXERCISE_SERVER = "localhost:50051"
UNREACHABLE_SERVER = "localhost:50099"


def demo_deadline_exceeded() -> None:
    """TODO: trigger and inspect DEADLINE_EXCEEDED.

    Steps:
    1. Open channel to UNREACHABLE_SERVER
    2. Create ChatServiceStub
    3. Call SendMessage with timeout=0.2 and wait_for_ready=True
    4. Catch grpc.RpcError and print code/details
    """
    print("\n[Deadline]")
    # TODO


def demo_invalid_argument() -> None:
    """TODO: call SendMessage with empty content and inspect status code/details."""
    print("\n[Error]")
    with grpc.insecure_channel(EXERCISE_SERVER) as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        # TODO: call stub.SendMessage with content=""
        # TODO: catch grpc.RpcError and print code/details


def main() -> None:
    demo_deadline_exceeded()
    demo_invalid_argument()


if __name__ == "__main__":
    main()
