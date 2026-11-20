"""Extract the Solution blocks from the root README and write them to disk.

Used by CI (and by anyone who wants to check the published solutions still
work) to verify that the code participants are told to copy actually runs.

Usage, from the workshop/ directory:
    python infrastructure/apply_readme_solutions.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORKSHOP = Path(__file__).resolve().parents[1]
README = WORKSHOP.parent / "README.md"

# Solution number -> file it belongs to, relative to workshop/.
TARGETS = {
    "1": "exercises/01_protocol_buffers/chat.proto",
    "2": "exercises/server.py",
    "3": "exercises/server.py",
    "4": "exercises/04_unary_client/client_starter.py",
    "5": "exercises/05_streaming/streaming_starter.py",
    "5-server": "exercises/server.py",
    "6": "exercises/06_deadlines_cancellation_errors/deadlines_starter.py",
    "7": "exercises/07_final_chat_client/client.py",
}

# "5-server" is the complete server.py (all four methods) and supersedes
# Solutions 2 and 3, which target the same file, so it must be applied after
# them.
ORDER = ["1", "2", "3", "4", "5", "5-server", "6", "7"]


def extract() -> dict[str, str]:
    text = README.read_text(encoding="utf-8")
    found: dict[str, str] = {}
    pattern = re.compile(
        r"<summary>.*?Solution\s*(\d+(?:-server)?).*?</summary>(.*?)</details>",
        re.I | re.S,
    )
    for match in pattern.finditer(text):
        number, body = match.group(1), match.group(2)
        blocks = re.findall(r"```(?:\w+)?\n(.*?)```", body, re.S)
        if not blocks:
            continue
        # The solution is the first (and only) fenced block in the section.
        found[number] = blocks[0]
    return found


def main() -> int:
    solutions = extract()
    missing = [n for n in ORDER if n not in solutions]
    if missing:
        print(f"ERROR: no Solution block found for: {', '.join(missing)}")
        return 1

    for number in ORDER:
        target = WORKSHOP / TARGETS[number]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(solutions[number], encoding="utf-8")
        print(f"Solution {number} -> {TARGETS[number]}")

    # Exercise 7's client is also the CLI used by poe client-* tasks.
    cli = WORKSHOP / "exercises/client.py"
    cli.write_text(solutions["7"], encoding="utf-8")
    print(f"Solution 7 -> exercises/client.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
