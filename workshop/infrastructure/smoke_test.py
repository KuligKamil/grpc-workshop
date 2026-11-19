"""Run the commands participants actually type, and check they work.

The test suite builds its servers in-process, so it never exercises
`poe server` plus a `poe client-*` CLI — the path every participant takes
first. Three defects in those scripts (a stripped import, a missing
`if __name__ == "__main__"`) passed the whole suite and only showed up when
someone ran them by hand. This closes that gap.

Expects the README solutions to be applied already (so the server works).

Usage, from the workshop/ directory:
    python infrastructure/smoke_test.py
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

WORKSHOP = Path(__file__).resolve().parents[1]
PORT = 50051
HOST = "127.0.0.1"


# `poe server*` runs generate-exercises first, which *deletes* the stubs before
# writing them. A client starting in that window dies with ImportError, so wait
# for the generated files to be back as well as for the port.
_STUBS = (
    WORKSHOP / "exercises" / "generated" / "chat_pb2.py",
    WORKSHOP / "exercises" / "generated" / "chat_pb2_grpc.py",
)


def _wait_for_server(port: int, timeout: float = 60.0) -> bool:
    """Poll until the port accepts connections and the stubs exist again."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        listening = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            listening = sock.connect_ex((HOST, port)) == 0
        if listening and all(path.exists() for path in _STUBS):
            # The import machinery can still be mid-write; give it a moment.
            time.sleep(0.5)
            return True
        time.sleep(0.5)
    return False


def _run(task: str, *args: str, timeout: float = 90.0) -> tuple[int, str]:
    """Run a poe task and return (exit code, combined output)."""
    completed = subprocess.run(
        [sys.executable, "-m", "poethepoet", task, *args],
        cwd=WORKSHOP,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return completed.returncode, completed.stdout + completed.stderr


class Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, label: str, condition: bool, detail: str = "") -> None:
        if condition:
            print(f"  PASS  {label}")
        else:
            print(f"  FAIL  {label}")
            if detail:
                print("        " + detail.strip().replace("\n", "\n        "))
            self.failures.append(label)


def main() -> int:
    checks = Checks()

    print("Starting `poe server` ...")
    server = subprocess.Popen(
        [sys.executable, "-m", "poethepoet", "server"],
        cwd=WORKSHOP,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        if not _wait_for_server(PORT):
            output = ""
            if server.poll() is not None and server.stdout:
                output = server.stdout.read()
            print("FAIL  `poe server` never started listening")
            if output:
                print(output)
            return 1
        print(f"  PASS  `poe server` is listening on :{PORT}")

        # The reference CLI, used for smoke tests during exercises 3-5.
        code, out = _run("client-send", "--room", "smoke", "--user", "alice", "hello")
        checks.expect("poe client-send", code == 0 and "status=ok" in out, out)

        code, out = _run("client-bulk", "--room", "smoke", "--count", "3")
        checks.expect("poe client-bulk", code == 0 and "sent=3" in out, out)

        code, out = _run("client-history", "--room", "smoke", "--limit", "10")
        checks.expect("poe client-history", code == 0 and "hello" in out, out)

        # The participant's own exercise-7 client.
        code, out = _run("final-send", "--room", "smoke", "--user", "bob", "from final")
        checks.expect("poe final-send", code == 0 and "status=ok" in out, out)

        code, out = _run("final-history", "--room", "smoke", "--limit", "10")
        checks.expect("poe final-history", code == 0 and "from final" in out, out)

        # Starter scripts: these are the files `ruff --fix` broke twice.
        code, out = _run("starter-04")
        checks.expect("poe starter-04", code == 0 and "status" in out, out)

        code, out = _run("starter-05")
        checks.expect(
            "poe starter-05",
            code == 0 and "[Unary]" in out and "Sent:" in out,
            out,
        )

        code, out = _run("starter-06")
        checks.expect(
            "poe starter-06",
            code == 0 and "DEADLINE_EXCEEDED" in out and "INVALID_ARGUMENT" in out,
            out,
        )
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()

    # The bonus servers replace the normal one, so run them separately.
    for task, label in (("server-broadcast", "poe server-broadcast"),):
        print(f"Starting `poe {task}` ...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "poethepoet", task],
            cwd=WORKSHOP,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            if not _wait_for_server(PORT):
                checks.expect(label, False, "never started listening")
                continue
            code, out = _run("final-send", "--room", "smoke", "--user", "a", "bcast")
            checks.expect(label, code == 0 and "status=ok" in out, out)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()

    # The intercepted server rejects unauthenticated calls, so its own demo
    # client is the only thing that can talk to it.
    print("Starting `poe server-intercepted` ...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "poethepoet", "server-intercepted"],
        cwd=WORKSHOP,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        if _wait_for_server(PORT):
            code, out = _run("client-intercepted")
            checks.expect(
                "poe client-intercepted",
                code == 0 and "status=ok" in out and "UNAUTHENTICATED" in out,
                out,
            )
        else:
            checks.expect("poe server-intercepted", False, "never started listening")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    print()
    if checks.failures:
        print(f"{len(checks.failures)} smoke check(s) failed:")
        for failure in checks.failures:
            print(f"  - {failure}")
        return 1
    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
