#!/bin/sh
set -e

# Regenerate protobuf stubs from the host-mounted chat.proto on every start,
# so participants never run against stale generated code and don't need a
# local protoc install.
#
# Failure is reported but not fatal: on a clean repo chat.proto still has
# TODOs, and the participant must still be able to get a shell.
if ! uv run poe generate-exercises; then
    echo "entrypoint: generate-exercises failed (see the error above)." >&2
    echo "entrypoint: continuing — finish Exercise 01, then re-run it." >&2
fi

exec uv run "$@"
