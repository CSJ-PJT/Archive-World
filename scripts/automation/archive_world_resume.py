#!/usr/bin/env python3
"""Print the exact checkpoint contract for a human or approved resume runner."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--state", required=True, type=Path)
args = parser.parse_args()
state = json.loads(args.state.read_text(encoding="utf-8"))
print(json.dumps({
    "branch": state["branch"], "head": state["head"], "checkpoint": state.get("lastCheckpoint"),
    "completed": state.get("completedTracks", []), "pending": state.get("pendingTracks", []),
    "blocked": state.get("blockedTracks", []), "lastError": state.get("lastError"),
}, indent=2))
