# Agent notes

## Don't commit generated protobuf/gRPC stubs

`workshop/exercises/generated/chat_pb2*.py(i)` are build artifacts produced by
`poe generate-exercises` (see `workshop/pyproject.toml`). Every test task
(`poe test-exercises`, `poe test-0N`), `poe server*`, and the CI workflow
regenerate them from `chat.proto` before use, so they must never be committed.

If you run any `poe` task locally that regenerates them, check `git status`
before committing and make sure they aren't staged.
