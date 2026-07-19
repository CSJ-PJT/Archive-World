#!/usr/bin/env python3
"""Atomically mark direct-session activity without impersonating a worker PID."""
import argparse
import json
import os
import time
from pathlib import Path


def atomic_write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("start", "heartbeat", "idle"))
    parser.add_argument("--state", type=Path, default=Path("state/archive-world-marathon.json"))
    parser.add_argument("--track")
    args = parser.parse_args()
    state = json.loads(args.state.read_text(encoding="utf-8"))
    now = time.time()
    state["directSessionStatus"] = "DIRECT_SESSION_IDLE" if args.action == "idle" else "DIRECT_SESSION_RUNNING"
    if args.action != "idle":
        state["directSessionLastActivity"] = now
    if args.track:
        state["directSessionTrack"] = args.track
    atomic_write(args.state, state)
    print(json.dumps({"status": state["directSessionStatus"], "track": state.get("directSessionTrack"), "at": now}))


if __name__ == "__main__":
    main()
