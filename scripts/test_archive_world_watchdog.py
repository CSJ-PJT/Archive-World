#!/usr/bin/env python3
"""Dry-run decision fixtures for the local Archive World watchdog."""
import importlib.util
import os
from pathlib import Path

SOURCE = Path(__file__).with_name("automation") / "archive_world_watchdog.py"
SPEC = importlib.util.spec_from_file_location("watchdog", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

CONFIG = {"branch": "feat/archive-visual-foundation-v1", "staleSeconds": 600}
SNAPSHOT = {"branch": CONFIG["branch"], "head": "3227afe", "status": ["?? scripts/blender/architecture_factory_v3.py"]}
OUTPUT = {"fileCount": 3, "bytes": 9}


def state(**changes):
    value = {
        "status": "RUNNING", "head": "3227afe", "heartbeat": 0,
        "pendingTracks": ["render-studio"], "activePid": None,
        "knownWorktree": SNAPSHOT["status"],
        "watchSnapshot": {"logBytes": 12, "output": OUTPUT, "head": "3227afe", "status": SNAPSHOT["status"]},
    }
    value.update(changes)
    return value


def expect(label, value, wanted):
    actual = MODULE.decide(value, CONFIG, SNAPSHOT, 700, 0, 12, OUTPUT)[0]
    assert actual == wanted, f"{label}: wanted {wanted}, got {actual}"


expect("running process", state(activePid=1), "RUNNING")
expect("fresh heartbeat", state(heartbeat=200), "RUNNING")
expect("stale idle", state(), "IDLE")
expect("waiting approval", state(status="WAITING_APPROVAL"), "SKIP")
expect("blocked", state(status="BLOCKED"), "SKIP")
expect("complete", state(status="COMPLETE"), "SKIP")
expect("empty queue", state(pendingTracks=[]), "SKIP")
assert MODULE.decide(state(activePid=os.getpid()), CONFIG, SNAPSHOT, 700, 0, 12, OUTPUT)[0] == "RUNNING"
assert MODULE.decide(state(activePid=999999), CONFIG, SNAPSHOT, 700, 0, 12, OUTPUT)[0] == "IDLE"
changed = dict(SNAPSHOT, status=[" M docs/changed.md"])
assert MODULE.decide(state(), CONFIG, changed, 700, 0, 12, OUTPUT)[0] == "BLOCK"
assert MODULE.decide(state(), CONFIG, changed, 700, 0, 12, OUTPUT)[1] == "worktree-changed"

restart_config = dict(CONFIG, maxRestart24h=6, maxRestartPerTrack=2, cooldownSeconds=1800, resumeCommand=["not-installed"])
restart_state = state(restartHistory=[{"track": "render-studio", "at": 100}, {"track": "render-studio", "at": 200}])
assert MODULE.start_resume(restart_config, restart_state, 700)[0] == "track-restart-limit"
daily_state = state(restartHistory=[{"track": f"track-{n}", "at": 100} for n in range(6)])
assert MODULE.start_resume(restart_config, daily_state, 700)[0] == "daily-restart-limit"
cooldown_state = state(restartHistory=[{"track": "render-studio", "at": 650}])
assert MODULE.start_resume(restart_config, cooldown_state, 700)[0] == "cooldown"
unavailable_state = state()
assert MODULE.start_resume(restart_config, unavailable_state, 700)[0] == "resume-command-unavailable"
print("archive world watchdog decision fixtures PASS")
