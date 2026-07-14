"""CLI client for the Chat gRPC service."""
import grpc
import typer

from exercises.generated import chat_pb2, chat_pb2_grpc

app = typer.Typer(help="Chat service client")


def _stub(host: str, port: int) -> tuple[grpc.Channel, chat_pb2_grpc.ChatServiceStub]:
    channel = grpc.insecure_channel(f"{host}:{port}")
    return channel, chat_pb2_grpc.ChatServiceStub(channel)


@app.command()
def send(
    message: str = typer.Argument(..., help="Message text to send"),
    room: str = typer.Option("general", "--room", "-r", help="Chat room ID"),
    user: str = typer.Option("alice", "--user", "-u", help="Username"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Exercise 07 — TODO: send a single message (unary RPC)."""
    # TODO:
    # 1) open insecure channel
    # 2) create stub
    # 3) call SendMessage with MessageRequest(room_id, user, content)
    # 4) print response.message_id and response.status
    # 5) handle grpc.RpcError with code/details
    raise NotImplementedError("Exercise 07: implement send()")


@app.command()
def history(
    room: str = typer.Option("general", "--room", "-r"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max messages to fetch"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Exercise 07 — TODO: fetch message history (server-streaming RPC)."""
    # TODO:
    # 1) open insecure channel
    # 2) create stub
    # 3) call GetHistory with HistoryRequest(room_id, limit)
    # 4) iterate stream and print each message
    # 5) handle grpc.RpcError with code/details
    raise NotImplementedError("Exercise 07: implement history()")


@app.command()
def chat(
    room: str = typer.Option("general", "--room", "-r"),
    user: str = typer.Option("alice", "--user", "-u"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Exercise 07 — TODO: real-time chat (bidirectional streaming RPC)."""
    # TODO:
    # 1) define a request generator reading input lines
    # 2) yield MessageRequest(room_id, user, content)
    # 3) open insecure channel and create stub
    # 4) iterate stub.Chat(generator) and print replies
    # 5) handle KeyboardInterrupt/EOFError and grpc CANCELLED cleanly
    raise NotImplementedError("Exercise 07: implement chat()")
