# gRPC Chat Workshop — exercises

This is the working directory for the workshop. Run every command below from
here (`workshop/`).

The full workshop material — theory, live coding, all seven exercises and their
solutions — is in the [main README](../README.md).

## Layout

| Path | What it is |
|------|------------|
| `exercises/01_protocol_buffers/chat.proto` | the service contract you fill in (Exercise 1) |
| `exercises/server.py` | the servicer you implement (Exercises 2, 3, 5) |
| `exercises/*_starter.py` | starter scripts for Exercises 4–6 |
| `exercises/07_final_chat_client/client.py` | the final CLI client (Exercise 7) |
| `exercises/generated/` | generated protobuf/gRPC code — never edit by hand |
| `exercises/0N_*/README.md` | the instructions for exercise N |
| `tests/exercises/` | the tests that check your work |

## Common commands

```bash
poe generate-exercises   # compile chat.proto into exercises/generated/
poe server               # start the chat server on :50051 (regenerates first)
poe test-exercises       # run all tests
poe test-01 ... test-07  # run the tests for one exercise
poe lint                 # ruff
```

On a clean checkout `poe test-exercises` reports **34 failed, 3 passed** — the
tests are written to fail until you implement each exercise.

## Setup

```bash
uv sync
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
```

Or use Docker, which needs no local Python:

```bash
docker compose run --rm workshop poe test-exercises
```

See [How to prepare for the workshop](../README.md#how-to-prepare-for-the-workshop)
for the details, including how to reach the server from a client container.
