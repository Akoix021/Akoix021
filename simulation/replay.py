"""Reconstruct the setpoint sequence stored in the archived UDP client."""

import argparse
import json
from pathlib import Path
import socket
import time


ADDRESS = ("127.0.0.1", 12345)
SEQUENCE = Path(__file__).with_name("sequence.json")


def commands(full):
    """Yield (setpoints, seconds until the next packet) in playback order."""
    sequence = json.loads(SEQUENCE.read_text(encoding="utf-8"))
    if full:
        yield sequence["initial"], 1.0
    for phase in sequence["phases"]:
        if not full and phase["group"] != "fixture":
            continue
        targets = phase["targets"]
        steps = phase["steps"]
        values = {name: start for name, (start, end) in targets.items()}
        yield values.copy(), 1.0
        increments = {name: (end - start) / steps for name, (start, end) in targets.items()}
        for step in range(steps):
            for name in values:
                values[name] += increments[name]
            delay = 0.1 + (phase["after"] if step == steps - 1 else 0)
            yield values.copy(), delay


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send the recorded setpoints to a local viewer.")
    parser.add_argument("--full", action="store_true", help="include the arm and hand")
    args = parser.parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for values, delay in commands(args.full):
            sender.sendto(json.dumps(values).encode("utf-8"), ADDRESS)
            time.sleep(delay)
