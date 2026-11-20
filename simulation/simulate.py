"""Play an archived motion sequence in MuJoCo, or drive the viewer over local UDP."""

import argparse
from contextlib import nullcontext
import json
import math
from pathlib import Path
import socket
import time

import mujoco
import numpy as np

from replay import ADDRESS, commands


FIXTURE = Path(__file__).with_name("fixture.xml")


def apply_controls(data, ids, values):
    if not isinstance(values, dict):
        raise ValueError("Expected a JSON object of actuator setpoints")
    for name, value in values.items():
        if name not in ids or type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError(f"Invalid setpoint for {name!r}")
    for name, value in values.items():
        data.ctrl[ids[name]] = value


def step_for(model, data, viewer, duration):
    tick = model.opt.timestep
    remaining = round(duration / tick)
    if viewer is None:
        mujoco.mj_step(model, data, nstep=remaining)
        return True
    chunk = max(1, round(1 / (60 * tick)))
    start = time.monotonic()
    stepped = 0
    while remaining > 0 and viewer.is_running():
        count = min(chunk, remaining)
        mujoco.mj_step(model, data, nstep=count)
        viewer.sync()
        stepped += count
        remaining -= count
        time.sleep(max(0, start + stepped * tick - time.monotonic()))
    return remaining == 0


def listen(model, data, viewer, ids):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(ADDRESS)
        receiver.setblocking(False)
        print(f"Listening on {ADDRESS[0]}:{ADDRESS[1]}", flush=True)
        while viewer.is_running():
            try:
                packet, _ = receiver.recvfrom(16384)
                apply_controls(data, ids, json.loads(packet))
            except BlockingIOError:
                pass
            except (ValueError, OverflowError) as error:
                print(f"Skipped a control packet: {error}")
            step_for(model, data, viewer, 1 / 60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, help="path to the archived full main.xml")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--headless", action="store_true", help="play without a graphics window")
    mode.add_argument("--listen", action="store_true", help="wait for replay.py in a second terminal")
    args = parser.parse_args()
    model = mujoco.MjModel.from_xml_path(str((args.model or FIXTURE).resolve()))
    data = mujoco.MjData(model)
    ids = {model.actuator(i).name: i for i in range(model.nu)}
    context = nullcontext()
    if not args.headless:
        from mujoco import viewer
        context = viewer.launch_passive(model, data)
    with context as window:
        if args.listen:
            listen(model, data, window, ids)
            return
        packet_count = 0
        for values, delay in commands(full=args.model is not None):
            apply_controls(data, ids, values)
            if not step_for(model, data, window, delay):
                return
            packet_count += 1
        if not np.isfinite(data.qpos).all() or any(data.warning.number):
            raise RuntimeError(f"Simulation warning or non-finite joint positions: {data.warning.number}")
        print(f"Played {packet_count} commands over {data.time:.3f} simulated seconds "
              f"with {model.nu} actuators.")


if __name__ == "__main__":
    main()
