"""CLI client for the Chat gRPC service."""

import sys

import grpc
import typer

from exercises.generated import chat_pb2, chat_pb2_grpc

# Windows consoles default to cp1252, which cannot encode the checkmarks and
# arrows below, so printing them raises UnicodeEncodeError. Ask for UTF-8.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

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
    """Exercise 07 solution: send a single message (unary RPC)."""
    channel, stub = _stub(host, port)
    with channel:
        try:
            response = stub.SendMessage(
                chat_pb2.MessageRequest(room_id=room, user=user, content=message)
            )
            typer.echo(f"✓ Sent  id={response.message_id}  status={response.status}")
        except grpc.RpcError as error:
            typer.echo(f"✗ {error.code()}: {error.details()}", err=True)
            raise typer.Exit(1)


@app.command()
def history(
    room: str = typer.Option("general", "--room", "-r"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max messages to fetch"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Exercise 07 solution: fetch message history (server-streaming RPC)."""
    channel, stub = _stub(host, port)
    with channel:
        try:
            stream = stub.GetHistory(chat_pb2.HistoryRequest(room_id=room, limit=limit))
            for message_item in stream:
                typer.echo(f"[{message_item.user}] {message_item.content}")
        except grpc.RpcError as error:
            typer.echo(f"✗ {error.code()}: {error.details()}", err=True)
            raise typer.Exit(1)


@app.command()
def bulk(
    room: str = typer.Option("general", "--room", "-r", help="Chat room ID"),
    user: str = typer.Option("alice", "--user", "-u", help="Username"),
    count: int = typer.Option(5, "--count", "-n", help="How many messages to send"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Send several messages in one call (client-streaming RPC)."""
    channel, stub = _stub(host, port)
    with channel:

        def _requests():
            for index in range(count):
                yield chat_pb2.MessageRequest(
                    room_id=room, user=user, content=f"bulk {index}"
                )

        try:
            response = stub.SendBulkMessages(_requests())
            typer.echo(
                f"✓ Sent  sent={response.messages_sent}  "
                f"failed={response.messages_failed}"
            )
        except grpc.RpcError as error:
            typer.echo(f"✗ {error.code()}: {error.details()}", err=True)
            raise typer.Exit(1)


@app.command()
def chat(
    room: str = typer.Option("general", "--room", "-r"),
    user: str = typer.Option("alice", "--user", "-u"),
    host: str = typer.Option("localhost", hidden=True),
    port: int = typer.Option(50051, hidden=True),
) -> None:
    """Exercise 07 solution: real-time bidirectional chat."""

    def _requests():
        typer.echo("Connected! Type messages and press Enter. Ctrl-C to quit.")
        try:
            while True:
                line = input(f"{user}> ").strip()
                if line:
                    yield chat_pb2.MessageRequest(room_id=room, user=user, content=line)
        except (KeyboardInterrupt, EOFError):
            return

    channel, stub = _stub(host, port)
    with channel:
        try:
            for message_item in stub.Chat(_requests()):
                typer.echo(f"  ← [{message_item.user}] {message_item.content}")
        except grpc.RpcError as error:
            if error.code() != grpc.StatusCode.CANCELLED:
                typer.echo(f"✗ {error.code()}: {error.details()}", err=True)
