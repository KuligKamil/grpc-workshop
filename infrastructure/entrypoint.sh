#!/bin/sh
set -e

# Auto-generate protobuf stubs from both proto sources.
# Running this on every container start keeps generated files in sync with
# the host-mounted source, so participants don't need a local protoc install.

generate() {
    src_dir="$1"
    out_dir="$2"
    proto_file="$3"

    if [ -f "${src_dir}/${proto_file}" ]; then
        uv run python -m grpc_tools.protoc \
            -I "${src_dir}" \
            --python_out="${out_dir}" \
            --grpc_python_out="${out_dir}" \
            "${src_dir}/${proto_file}" 2>/dev/null || true

        # grpc_tools emits absolute-style import; fix it to relative so the
        # generated package works when imported as exercises.generated or
        # solutions.generated.
        grpc_out="${out_dir}/$(basename "${proto_file}" .proto)_pb2_grpc.py"
        if [ -f "${grpc_out}" ]; then
            uv run python -c "
import pathlib, re
f = pathlib.Path('${grpc_out}')
txt = f.read_text()
fixed = re.sub(r'^import (${proto_file%.proto}_pb2) as', r'from . import \1 as', txt, flags=re.MULTILINE)
if fixed != txt:
    f.write_text(fixed)
" 2>/dev/null || true
        fi
    fi
}
generate "exercises/01_protocol_buffers" "exercises/generated" "chat.proto"
generate "solutions/01_protocol_buffers" "solutions/generated" "chat.proto"

exec uv run "$@"
