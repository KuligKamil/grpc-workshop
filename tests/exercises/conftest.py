from concurrent import futures

import grpc
import pytest

_SKIP_MSG = (
    "Generated gRPC code not found — complete Exercise 01 "
    "and run: poe generate-exercises"
)


@pytest.fixture(scope="session")
def grpc_addr():
    try:
        from exercises.generated import chat_pb2_grpc
        from exercises.server import ChatServicer
    except ImportError:
        pytest.skip(_SKIP_MSG)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    port = server.add_insecure_port("[::]:0")
    server.start()
    yield f"localhost:{port}"
    server.stop(grace=None)


@pytest.fixture
def stub(grpc_addr):
    from exercises.generated import chat_pb2_grpc

    with grpc.insecure_channel(grpc_addr) as channel:
        yield chat_pb2_grpc.ChatServiceStub(channel)
