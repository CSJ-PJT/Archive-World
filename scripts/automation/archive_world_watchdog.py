#!/usr/bin/env python3
"""Archive World local idle watchdog.

This is deliberately a *local process supervisor*, not a ChatGPT integration.
It never restarts a completed, approval-gated, blocked, dirty, or different-branch
run.  State is written atomically so an operator can resume from the last
checkpoint after reboot.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GATED = {"COMPLETE", "WAITING_APPROVAL", "BLOCKED", "GATE_WAITING"}
ACTIVE_NAMES = ("blender", "blender.exe", "node", "node.exe", "python", "python3", "python.exe")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def process_alive(pid: int | None) -> bool:
    return bool(pid and pid > 0 and Path(f"/proc/{pid}").exists())


def active_children() -> list[dict[str, str]]:
    """Return relevant local workers. The watchdog itself is excluded by caller."""
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,comm=,args="], text=True, capture_output=True, check=False
    )
    children: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 3:
            continue
        pid, ppid, command = parts[:3]
        args = parts[3] if len(parts) > 3 else command
        if command.lower() in ACTIVE_NAMES and "archive_world_watchdog.py" not in args:
            children.append({"pid": pid, "ppid": ppid, "command": command, "args": args[:240]})
    return children


def git_snapshot(repo: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False).stdout.strip()

    return {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "--short", "HEAD"),
        "status": git("status", "--porcelain=v1").splitlines(),
    }


def tree_metrics(root: Path) -> dict[str, int]:
    count = size = 0
    if root.exists():
        for item in root.rglob("*"):
            if item.is_file():
                count += 1
                size += item.stat().st_size
    return {"fileCount": count, "bytes": size}


def decide(state: dict[str, Any], config: dict[str, Any], snapshot: dict[str, Any], now: float,
           child_count: int, log_size: int, output: dict[str, int]) -> tuple[str, str]:
    """Pure decision helper; covered by dry-run fixtures."""
    if state.get("lifecycle", "RUNNING") in GATED:
        return "SKIP", f"gated-lifecycle:{state.get('lifecycle')}"
    if not state.get("pendingTracks"):
        return "SKIP", "empty-queue"
    if snapshot["branch"] != config["branch"] or snapshot["head"] != state.get("head"):
        return "BLOCK", "branch-or-head-changed"
    known = state.get("knownWorktree", snapshot["status"])
    if snapshot["status"] != known:
        return "BLOCK", "worktree-changed"
    if process_alive(state.get("activePid")) or child_count:
        return "RUNNING", "active-process"
    if state.get("authStatus") == "AUTH_BLOCKED":
        return "AUTH_BLOCKED", "resume-transport-auth-blocked"
    heartbeat_age = now - float(state.get("workerHeartbeat", 0))
    previous = state.get("watchSnapshot", {})
    stable = (
        previous.get("logBytes") == log_size
        and previous.get("output") == output
        and previous.get("head") == snapshot["head"]
        and previous.get("status") == snapshot["status"]
    )
    if heartbeat_age < config["staleSeconds"]:
        return "RUNNING", "fresh-heartbeat"
    if not stable:
        return "RUNNING", "activity-observed"
    return "IDLE", "all-idle-signals-stale"


def start_resume(config: dict[str, Any], state: dict[str, Any], now: float) -> tuple[str, int | None]:
    track = state["pendingTracks"][0]
    history = [entry for entry in state.get("restartHistory", []) if now - entry["at"] < 86400]
    same_track = [entry for entry in history if entry["track"] == track]
    if len(history) >= config["maxRestart24h"]:
        state["authStatus"] = "AUTH_BLOCKED"
        state["lastTransportError"] = "daily-restart-limit-after-resume-transport-failure"
        return "daily-restart-limit", None
    if len(same_track) >= config["maxRestartPerTrack"]:
        state["authStatus"] = "AUTH_BLOCKED"
        state["lastTransportError"] = "restart-limit-after-resume-transport-failure"
        return "track-restart-limit", None
    if same_track and now - same_track[-1]["at"] < config["cooldownSeconds"]:
        return "cooldown", None
    command = config.get("resumeCommand", [])
    if not command or not shutil_which(command[0]):
        state["authStatus"] = "AUTH_BLOCKED"
        state["lastTransportError"] = "resume-command-unavailable"
        return "resume-command-unavailable", None
    checkpoint = state.get("lastCheckpoint", "initial")
    prompt = (
        "Resume Archive World Marathon exactly from its checkpoint. "
        f"branch={state['branch']}; head={state['head']}; checkpoint={checkpoint}; track={track}; "
        f"completed={','.join(state.get('completedTracks', []))}; blocked={','.join(state.get('blockedTracks', []))}. "
        "Do not change canonical/layout/runtime/main. No main merge, git add -A, reset, clean, or force push. "
        "Continue only the next independent track and record a checkpoint. "
        f"Before work, send exactly one recovery notification through the configured Slack runner to "
        f"{config.get('slackRecoveryChannel', 'the Archive World status channel')}: branch, checkpoint, resumed track, "
        "old heartbeat, new PID, and restart count. Do not expose credentials."
    )
    proc = subprocess.Popen([*command, prompt], cwd=config["repo"], start_new_session=True)
    state["activePid"] = proc.pid
    state["workerHeartbeat"] = now
    state["workerStatus"] = "WORKER_RUNNING"
    state.setdefault("restartHistory", []).append({"track": track, "at": now, "pid": proc.pid})
    return "resumed", proc.pid


def shutil_which(command: str) -> str | None:
    # Avoid importing platform-specific launch helpers; PATH lookup is enough.
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def run(config_path: Path, dry_run: bool, once: bool) -> int:
    config = read_json(config_path)
    state_path = ROOT / config["state"]
    pid_path = ROOT / config["pidFile"]
    log_path = ROOT / config["log"]
    marathon_log_path = ROOT / config["marathonLog"]
    existing = int(pid_path.read_text().strip()) if pid_path.exists() and pid_path.read_text().strip().isdigit() else None
    if existing and existing != os.getpid() and process_alive(existing):
        print(json.dumps({"action": "duplicate-watchdog", "pid": existing}))
        return 0
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="utf-8")
    try:
        while True:
            now = time.time()
            state = read_json(state_path)
            snapshot = git_snapshot(Path(config["repo"]))
            children = active_children()
            output = tree_metrics(Path(config["generatedRoot"]))
            marathon_log_bytes = marathon_log_path.stat().st_size if marathon_log_path.exists() else 0
            active_worker = process_alive(state.get("activePid")) or bool(children)
            decision, reason = decide(state, config, snapshot, now, len(children), marathon_log_bytes, output)
            state["watchdogStatus"] = "WATCHDOG_RUNNING"
            state["workerStatus"] = "WORKER_RUNNING" if active_worker else "WORKER_IDLE"
            if active_worker:
                state["workerHeartbeat"] = now
            event: dict[str, Any] = {
                "at": now, "action": decision.lower(), "reason": reason, "track": (state.get("pendingTracks") or [None])[0],
                "workerHeartbeatAge": now - float(state.get("workerHeartbeat", 0)), "children": children,
                "output": output, "git": {"branch": snapshot["branch"], "head": snapshot["head"]}, "dryRun": dry_run,
            }
            if decision == "IDLE" and not dry_run and config.get("enabled", False):
                action, pid = start_resume(config, state, now)
                event["action"] = action
                event["newPid"] = pid
            if decision == "BLOCK":
                state["lifecycle"] = "BLOCKED"
                state["lastError"] = reason
            state["watchSnapshot"] = {"at": now, "logBytes": marathon_log_bytes, "output": output, "head": snapshot["head"], "status": snapshot["status"]}
            atomic_json(state_path, state)
            append_json(log_path, event)
            print(json.dumps(event, sort_keys=True))
            if once:
                return 0
            time.sleep(config["intervalSeconds"])
    finally:
        if pid_path.exists() and pid_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
            pid_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    return run(args.config, args.dry_run, args.once)


if __name__ == "__main__":
    raise SystemExit(main())
