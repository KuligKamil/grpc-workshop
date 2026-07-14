"""Entry point — `python -m exercises.main`."""

import typer

from exercises import client
from exercises.server import serve

app = typer.Typer(help="gRPC Chat Workshop CLI")

app.add_typer(client.app, name="client")


@app.command()
def server(
    port: int = typer.Option(50051, "--port", "-p", help="gRPC port"),
) -> None:
    """Start the gRPC chat server."""
    serve(port=port)


if __name__ == "__main__":
    app()
